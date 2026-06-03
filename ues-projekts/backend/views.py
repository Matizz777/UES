from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
import uuid
import pytz
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import activate
from django.shortcuts import redirect
from django.conf import settings

def set_language(request, language_code):
    if language_code in dict(settings.LANGUAGES):
        activate(language_code)
        request.session['django_language'] = language_code
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', language_code, max_age=365*24*60*60)
        return response
    return redirect('/')

def api_set_language(request):
    try:
        data = json.loads(request.body)
        language_code = data.get('language')
        
        if language_code in dict(settings.LANGUAGES):
            activate(language_code)
            request.session['django_language'] = language_code
            response = JsonResponse({'status': 'success'})
            response.set_cookie('django_language', language_code, max_age=365*24*60*60)
            return response
        
        return JsonResponse({'status': 'error', 'message': _('Invalid language')}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_user_from_token(token):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [token])
        row = cursor.fetchone()
    return row[0] if row else None

def create_notification(user_id, title, message):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
            [user_id, title, message]
        )

def get_service(service_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, price, description, duration_minutes, work_days, work_start, work_end, provider_id FROM services WHERE id = %s",
            [service_id]
        )
        row = cursor.fetchone()
    if not row:
        return None
    return {
        "id": row[0], "name": row[1], "price": float(row[2]),
        "description": row[3] or '',
        "duration_minutes": row[4] or 60,
        "work_days":  row[5] or '1,2,3,4,5',
        "work_start": str(row[6])[:5] if row[6] else '09:00',
        "work_end":   str(row[7])[:5] if row[7] else '17:00',
        "provider_id": row[8],
    }

def generate_slots(work_start, work_end, duration_minutes):
    slots = []
    fmt = "%H:%M"
    current = datetime.strptime(work_start, fmt)
    end     = datetime.strptime(work_end,   fmt)
    delta   = timedelta(minutes=int(duration_minutes))
    while current + delta <= end:
        slots.append(current.strftime(fmt))
        current += delta
    return slots

def get_booked_blocks(provider_id, date_str):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT res_time, res_end_time FROM reservations
            WHERE provider_id = %s AND res_date = %s
        """, [provider_id, date_str])
        rows = cursor.fetchall()
    blocks = []
    for r in rows:
        if r[0] and r[1]:
            blocks.append((str(r[0])[:5], str(r[1])[:5]))
    return blocks

def slot_overlaps(slot_start, slot_end, booked_blocks):
    fmt = "%H:%M"
    s = datetime.strptime(slot_start, fmt)
    e = datetime.strptime(slot_end,   fmt)
    for (bs, be) in booked_blocks:
        b_s = datetime.strptime(bs, fmt)
        b_e = datetime.strptime(be, fmt)
        if s < b_e and e > b_s:
            return True
    return False

def is_work_day(date_str, work_days):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    iso_weekday = str(d.isoweekday())
    allowed = [x.strip() for x in work_days.split(',')]
    return iso_weekday in allowed

def fmt_time(t):
    if not t: return ''
    return t.strftime("%H:%M") if hasattr(t, 'strftime') else str(t)[:5]

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            token = f"token-{username}"
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO auth_user
                    (username, email, password, roles, industry, description,
                     first_name, last_name, is_active, date_joined, session_token,
                     phone, address, reg_number)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """, [
                    username, data.get('email'),
                    make_password(data.get('password')),
                    data.get('roles', 3),
                    data.get('industry', ''), data.get('description', ''),
                    '', '', True, datetime.now(), token,
                    data.get('phone', ''),
                    data.get('address', ''),
                    data.get('reg_number', '')
                ])
                new_id = cursor.fetchone()[0]
            return JsonResponse({"id": new_id, "username": username,
                                 "roles": data.get('roles'), "token": token}, status=201)
        except Exception as e:
            print(f"DB ERROR: {e}")
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password, roles, session_token FROM auth_user WHERE username = %s",
                    [data.get('username')]
                )
                user = cursor.fetchone()
            if not user or not check_password(data.get('password'), user[2]):
                return JsonResponse({"error": _("Nepareizs lietotājvārds vai parole.")}, status=400)
            return JsonResponse({"id": user[0], "username": user[1],
                                 "roles": user[3], "token": user[4]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("POST only")}, status=405)

@csrf_exempt
def add_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO services
                    (name, price, description, provider_id, duration_minutes, work_days, work_start, work_end)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    data.get('name'), data.get('price'),
                    data.get('description', ''), data.get('provider_id'),
                    data.get('duration_minutes', 60),
                    data.get('work_days', '1,2,3,4,5'),
                    data.get('work_start', '09:00'),
                    data.get('work_end', '17:00'),
                ])
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            print(f"KĻŪDA: {e}")
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_my_services(request):
    provider_id = request.GET.get('provider_id')
    if not provider_id:
        return JsonResponse({"error": _("Nav provider_id")}, status=400)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, price, description, duration_minutes, work_days, work_start, work_end
                FROM services WHERE provider_id = %s ORDER BY id ASC
            """, [provider_id])
            rows = cursor.fetchall()
        result = [{
            "id": r[0], "name": r[1], "price": float(r[2]),
            "description": r[3] or '',
            "duration_minutes": r[4] or 60,
            "work_days":  r[5] or '1,2,3,4,5',
            "work_start": str(r[6])[:5] if r[6] else '09:00',
            "work_end":   str(r[7])[:5] if r[7] else '17:00',
        } for r in rows]
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def edit_service(request, service_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE services
                    SET name=%s, price=%s, description=%s,
                        duration_minutes=%s, work_days=%s, work_start=%s, work_end=%s
                    WHERE id=%s
                """, [
                    data.get('name'), data.get('price'),
                    data.get('description', ''),
                    data.get('duration_minutes', 60),
                    data.get('work_days', '1,2,3,4,5'),
                    data.get('work_start', '09:00'),
                    data.get('work_end', '17:00'),
                    service_id
                ])
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("PUT only")}, status=405)

@csrf_exempt
def delete_service(request, service_id):
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM services WHERE id = %s", [service_id])
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("DELETE only")}, status=405)

@csrf_exempt
def get_providers(request):
    search   = request.GET.get('search', '')
    industry = request.GET.get('industry', '')
    with connection.cursor() as cursor:
        query = "SELECT id, username, industry, description, phone, address, reg_number FROM auth_user WHERE roles = 2"
        params = []
        if search:
            query += " AND (username ILIKE %s OR description ILIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        if industry:
            query += " AND industry ILIKE %s"
            params.append(f'%{industry}%')
        cursor.execute(query, params)
        providers_rows = cursor.fetchall()
        result = []
        for row in providers_rows:
            p_id = row[0]
            cursor.execute("""
                SELECT id, name, price, description, duration_minutes, work_days, work_start, work_end
                FROM services WHERE provider_id = %s
            """, [p_id])
            s_rows = cursor.fetchall()
            p_services = [{
                "id": s[0], "name": s[1], "price": float(s[2]),
                "description": s[3] or '',
                "duration_minutes": s[4] or 60,
                "work_days":  s[5] or '1,2,3,4,5',
                "work_start": str(s[6])[:5] if s[6] else '09:00',
                "work_end":   str(s[7])[:5] if s[7] else '17:00',
            } for s in s_rows]
            result.append({
                "id": p_id, "username": row[1],
                "industry":    row[2] or _('Nav norādīta'),
                "description": row[3] or _('Nav apraksta.'),
                "phone":       row[4] or '',
                "address":     row[5] or '',
                "reg_number":  row[6] or '',
                "services":    p_services
            })
    return JsonResponse(result, safe=False)

@csrf_exempt
def get_occupied_times(request):
    service_id  = request.GET.get('service_id')
    provider_id = request.GET.get('provider_id')
    date_str    = request.GET.get('date')
    if not date_str:
        return JsonResponse({"available": [], "occupied": [], "all_slots": []}, safe=False)
    try:
        svc = get_service(service_id) if service_id else None
        if not svc:
            return JsonResponse({"available": [], "occupied": [], "all_slots": []}, safe=False)

        pid = provider_id or svc['provider_id']

        if not is_work_day(date_str, svc['work_days']):
            return JsonResponse({"available": [], "occupied": [], "all_slots": [], "not_work_day": True}, safe=False)

        all_slots     = generate_slots(svc['work_start'], svc['work_end'], svc['duration_minutes'])
        booked_blocks = get_booked_blocks(pid, date_str)

        occupied  = []
        available = []
        for slot in all_slots:
            slot_end = (datetime.strptime(slot, "%H:%M") + timedelta(minutes=int(svc['duration_minutes']))).strftime("%H:%M")
            if slot_overlaps(slot, slot_end, booked_blocks):
                occupied.append(slot)
            else:
                available.append(slot)

        return JsonResponse({"all_slots": all_slots, "occupied": occupied, "available": available}, safe=False)
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def save_booking(request):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({"error": _("Nav autorizācijas")}, status=401)
            token   = auth_header.split(' ')[1]
            data    = json.loads(request.body)
            user_id = get_user_from_token(token)
            if not user_id:
                return JsonResponse({"error": _("Sesija nederīga")}, status=401)

            service_id   = data.get('service_id')
            provider_id  = data.get('provider_id')
            service_name = data.get('service_name')
            booked_price = data.get('booked_price')
            date_str     = data.get('res_date')
            time_str     = data.get('res_time')[:5]

            svc      = get_service(service_id) if service_id else None
            duration = svc['duration_minutes'] if svc else 60

            end_str = (datetime.strptime(time_str, "%H:%M") + timedelta(minutes=int(duration))).strftime("%H:%M")

            booked_blocks = get_booked_blocks(provider_id, date_str)
            if slot_overlaps(time_str, end_str, booked_blocks):
                return JsonResponse({"error": _("Šis laiks jau ir rezervēts.")}, status=409)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reservations
                    (user_id, service_name, res_date, res_time, res_end_time, provider_id, service_id, booked_price, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, [user_id, service_name, date_str, time_str, end_str,
                    provider_id, service_id, booked_price, 'upcoming'])

            return JsonResponse({"message": _("Rezervācija saglabāta!")}, status=201)
        except Exception as e:
            import traceback; traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("POST only")}, status=405)

@csrf_exempt
def get_user_reservations(request):
    try:
        auth_header = request.headers.get('Authorization')
        token   = auth_header.split(' ')[1]
        role    = request.GET.get('role', '3')
        user_id = get_user_from_token(token)
        if not user_id:
            return JsonResponse({"error": _("Unauthorized")}, status=401)

        with connection.cursor() as cursor:
            if role == '2':
                cursor.execute("""
                    SELECT r.id, r.service_name, r.res_date, r.res_time, r.res_end_time,
                           u.username, '', r.booked_price, r.service_id, r.provider_id, r.status
                    FROM reservations r
                    JOIN auth_user u ON u.id = r.user_id
                    WHERE r.provider_id = %s AND r.status != 'cancelled'
                    ORDER BY r.res_date ASC, r.res_time ASC
                """, [user_id])
            else:
                cursor.execute("""
                    SELECT r.id, r.service_name, r.res_date, r.res_time, r.res_end_time,
                           '', p.username, r.booked_price, r.service_id, r.provider_id, r.status
                    FROM reservations r
                    LEFT JOIN auth_user p ON p.id = r.provider_id
                    WHERE r.user_id = %s AND r.status != 'cancelled'
                    ORDER BY r.res_date ASC, r.res_time ASC
                """, [user_id])
            rows = cursor.fetchall()

        return JsonResponse([{
            "id":            r[0],
            "service":       r[1],
            "date":          str(r[2]),
            "time":          fmt_time(r[3]),
            "end_time":      fmt_time(r[4]),
            "client_name":   r[5],
            "provider_name": r[6],
            "booked_price":  float(r[7]) if r[7] else None,
            "service_id":    r[8],
            "provider_id":   r[9],
            "status":        r[10],
        } for r in rows], safe=False)

    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_provider_calendar(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)

    year = request.GET.get('year')
    month = request.GET.get('month')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.service_name, r.res_date, r.res_time, r.res_end_time,
                       u.username AS client_name, r.booked_price
                FROM reservations r
                JOIN auth_user u ON u.id = r.user_id
                WHERE r.provider_id = %s
                  AND EXTRACT(YEAR FROM r.res_date) = %s
                  AND EXTRACT(MONTH FROM r.res_date) = %s
                  AND (r.status != 'cancelled' OR r.status IS NULL)
                ORDER BY r.res_date ASC, r.res_time ASC
            """, [user_id, year, month])
            rows = cursor.fetchall()

        return JsonResponse([{
            "id": r[0],
            "service": r[1],
            "date": str(r[2]),
            "start": fmt_time(r[3]),
            "end": fmt_time(r[4]),
            "client_name": r[5],
            "booked_price": float(r[6]) if r[6] else None,
        } for r in rows], safe=False)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def add_availability(request):
    if request.method == 'POST':
        return JsonResponse({"status": "ok"})
    
@csrf_exempt
def get_notifications(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token   = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, message, is_read, created_at
                FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 50
            """, [user_id])
            rows = cursor.fetchall()
        return JsonResponse([{
            "id":         r[0],
            "title":      r[1],
            "message":    r[2],
            "is_read":    r[3],
            "created_at": str(r[4])[:16],
        } for r in rows], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
 
@csrf_exempt
def mark_notifications_read(request):
    if request.method != 'POST':
        return JsonResponse({"error": _("POST only")}, status=405)
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token   = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE",
                [user_id]
            )
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
 
@csrf_exempt
def delete_notification(request, notif_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": _("DELETE only")}, status=405)
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notifications WHERE id = %s", [notif_id])
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def get_profile(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, roles, industry, description, 
                       first_name, last_name, phone, address, reg_number
                FROM auth_user 
                WHERE id = %s
            """, [user_id])
            row = cursor.fetchone()
        
        if not row:
            return JsonResponse({"error": _("User not found")}, status=404)
        
        return JsonResponse({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "roles": row[3],
            "industry": row[4] or '',
            "description": row[5] or '',
            "first_name": row[6] or '',
            "last_name": row[7] or '',
            "phone": row[8] or '',
            "address": row[9] or '',
            "reg_number": row[10] or '',
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def update_profile(request):
    if request.method != 'PUT':
        return JsonResponse({"error": _("PUT only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        data = json.loads(request.body)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE auth_user 
                SET email = %s, 
                    industry = %s, 
                    description = %s,
                    first_name = %s,
                    last_name = %s,
                    phone = %s,
                    address = %s,
                    reg_number = %s
                WHERE id = %s
            """, [
                data.get('email'),
                data.get('industry', ''),
                data.get('description', ''),
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('phone', ''),
                data.get('address', ''),
                data.get('reg_number', ''),
                user_id
            ])
        
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def change_password(request):
    if request.method != 'PUT':
        return JsonResponse({"error": _("PUT only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM auth_user WHERE id = %s",
                [user_id]
            )
            row = cursor.fetchone()
        
        if not row or not check_password(old_password, row[0]):
            return JsonResponse({"error": _("Nepareiza vecā parole")}, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE auth_user SET password = %s WHERE id = %s",
                [make_password(new_password), user_id]
            )
        
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def cancel_booking(request, booking_id):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body) if request.body else {}
            reason = data.get('reason', '')
            is_client_cancel = data.get('is_client_cancel', False)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT r.user_id, r.service_name, r.res_date, r.res_time,
                           r.provider_id, r.service_id, p.username, r.status
                    FROM reservations r
                    LEFT JOIN auth_user p ON p.id = r.provider_id
                    WHERE r.id = %s
                """, [booking_id])
                row = cursor.fetchone()
            
            if not row:
                return JsonResponse({"error": _("Pieraksts nav atrasts.")}, status=404)
            
            if row[7] == 'cancelled':
                return JsonResponse({"error": _("Pieraksts jau ir atcelts.")}, status=400)
            
            client_id = row[0]
            service_name = row[1]
            res_date = str(row[2])
            res_time = str(row[3])[:5]
            provider_id = row[4]
            service_id = row[5]
            provider_name = row[6] or _('Speciālists')
            
            with connection.cursor() as cursor2:
                cursor2.execute("SELECT username FROM auth_user WHERE id = %s", [client_id])
                client_username = cursor2.fetchone()[0]
            
            if is_client_cancel:
                title = f"{_('Pieraksts atcelts')} — {service_name}"
                message = f"{_('Klients')} {client_username} {_('ir atcēlis pierakstu')} ({service_name}, {res_date} {res_time})."
                create_notification(provider_id, title, message)
            else:
                title = f"{_('Pieraksts atcelts')} — {service_name}"
                message = f"{_('Jūsu pieraksts pie')} {provider_name} ({service_name}, {res_date} {res_time}) {_('ir atcelts.')}"
                if reason:
                    message += f"\n\n{_('Iemesls')}: {reason}"
                create_notification(client_id, title, message)
            
            with connection.cursor() as cursor:
                cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = %s", [booking_id])
            
            check_and_notify_waitlist(service_id, provider_id, res_date)
            
            return JsonResponse({"status": "success"})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("DELETE only")}, status=405)

@csrf_exempt
def reschedule_booking(request, booking_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            new_date = data.get('res_date')
            new_time = data.get('res_time')[:5]
            reason = data.get('reason', '')
            is_client_reschedule = data.get('is_client_reschedule', False)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT r.user_id, r.service_name, r.res_date, r.res_time,
                           r.provider_id, r.service_id, p.username, r.status
                    FROM reservations r
                    LEFT JOIN auth_user p ON p.id = r.provider_id
                    WHERE r.id = %s
                """, [booking_id])
                row = cursor.fetchone()
            
            if not row:
                return JsonResponse({"error": _("Pieraksts nav atrasts.")}, status=404)
            
            if row[7] == 'cancelled':
                return JsonResponse({"error": _("Pieraksts ir atcelts, to nevar pārcelt.")}, status=400)
            
            client_id = row[0]
            service_name = row[1]
            old_date = str(row[2])
            old_time = str(row[3])[:5]
            provider_id = row[4]
            service_id = row[5]
            provider_name = row[6] or _('Speciālists')
            
            with connection.cursor() as cursor2:
                cursor2.execute("SELECT username FROM auth_user WHERE id = %s", [client_id])
                client_username = cursor2.fetchone()[0]
            
            if is_client_reschedule:
                old_booking_datetime = datetime.strptime(f"{old_date} {old_time}", "%Y-%m-%d %H:%M")
                now = datetime.now()
                hours_until_booking = (old_booking_datetime - now).total_seconds() / 3600
                
                if hours_until_booking < 24 and hours_until_booking > 0:
                    return JsonResponse({
                        "error": _("Pierakstu var pārcelt ne vēlāk kā 24 stundas pirms tā sākuma. Atlikušas {} stundas.").format(int(hours_until_booking))
                    }, status=400)
            
            svc = get_service(service_id) if service_id else None
            duration = svc['duration_minutes'] if svc else 60
            end_time = (datetime.strptime(new_time, "%H:%M") + timedelta(minutes=int(duration))).strftime("%H:%M")
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT res_time, res_end_time FROM reservations
                    WHERE provider_id = %s AND res_date = %s AND id != %s
                """, [provider_id, new_date, booking_id])
                rows = cursor.fetchall()
            
            booked_blocks = [(str(r[0])[:5], str(r[1])[:5]) for r in rows if r[0] and r[1]]
            if slot_overlaps(new_time, end_time, booked_blocks):
                return JsonResponse({"error": _("Izvēlētais laiks pārklājas ar citu rezervāciju.")}, status=409)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE reservations
                    SET res_date = %s, res_time = %s, res_end_time = %s, status = 'rescheduled'
                    WHERE id = %s
                """, [new_date, new_time, end_time, booking_id])
            
            if is_client_reschedule:
                title = f"{_('Pieraksts pārcelts')} — {service_name}"
                message = (
                    f"{_('Klients')} {client_username} {_('ir pārcēlis pierakstu no')} {old_date} {old_time} "
                    f"{_('uz')} {new_date} {new_time}."
                )
                if reason:
                    message += f"\n\n{_('Iemesls')}: {reason}"
                create_notification(provider_id, title, message)
            else:
                title = f"{_('Pieraksts pārcelts')} — {service_name}"
                message = (
                    f"{_('Jūsu pieraksts pie')} {provider_name} ({service_name}) "
                    f"{_('ir pārcelts no')} {old_date} {old_time} "
                    f"{_('uz')} {new_date} {new_time}."
                )
                if reason:
                    message += f"\n\n{_('Iemesls')}: {reason}"
                create_notification(client_id, title, message)
            
            return JsonResponse({"status": "success"})
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": _("PATCH only")}, status=405)

@csrf_exempt
def add_to_waitlist(request):
    if request.method != 'POST':
        return JsonResponse({"error": _("POST only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        data = json.loads(request.body)
        service_id = data.get('service_id')
        provider_id = data.get('provider_id')
        preferred_date = data.get('preferred_date')
        preferred_time = data.get('preferred_time')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM waitlist 
                WHERE user_id = %s AND service_id = %s AND status = 'waiting'
            """, [user_id, service_id])
            if cursor.fetchone():
                return JsonResponse({"error": _("Jūs jau esat gaidīšanas sarakstā")}, status=400)
            
            cursor.execute("""
                INSERT INTO waitlist (user_id, service_id, provider_id, preferred_date, preferred_time)
                VALUES (%s, %s, %s, %s, %s)
            """, [user_id, service_id, provider_id, preferred_date, preferred_time])
        
        svc = get_service(service_id)
        create_notification(
            user_id, 
            _("Pievienots gaidīšanas sarakstam"), 
            _("Jūs esat pievienots gaidīšanas sarakstam pakalpojumam '{}'. Kad atbrīvosies vieta, jūs saņemsiet paziņojumu un jums būs 4 stundas, lai to apstiprinātu.").format(svc['name'])
        )
        
        return JsonResponse({"status": "added_to_waitlist"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def get_waitlist_status(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT w.id, w.service_id, s.name, w.preferred_date, w.preferred_time, 
                       w.created_at, w.status
                FROM waitlist w
                JOIN services s ON s.id = w.service_id
                WHERE w.user_id = %s AND w.status = 'waiting'
                ORDER BY w.created_at ASC
            """, [user_id])
            rows = cursor.fetchall()
        
        return JsonResponse([{
            "id": r[0],
            "service_id": r[1],
            "service_name": r[2],
            "preferred_date": str(r[3]) if r[3] else None,
            "preferred_time": str(r[4])[:5] if r[4] else None,
            "created_at": str(r[5]),
            "status": r[6],
        } for r in rows], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def remove_from_waitlist(request, waitlist_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": _("DELETE only")}, status=405)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM waitlist WHERE id = %s", [waitlist_id])
        return JsonResponse({"status": "removed"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def check_and_notify_waitlist(service_id, provider_id, available_date):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, user_id, preferred_date, preferred_time
            FROM waitlist 
            WHERE service_id = %s AND provider_id = %s AND status = 'waiting'
            ORDER BY created_at ASC
            LIMIT 1
        """, [service_id, provider_id])
        row = cursor.fetchone()
        
        if row:
            waitlist_id = row[0]
            user_id = row[1]
            
            token = str(uuid.uuid4())
            cursor.execute("""
                UPDATE waitlist SET notified_at = NOW(), status = 'notified'
                WHERE id = %s
            """, [waitlist_id])
            
            svc = get_service(service_id)
            create_notification(
                user_id,
                _("🏆 Vieta atbrīvojusies!"),
                _("Pakalpojumam '{}' ir atbrīvojusies vieta. Jums ir 4 stundas, lai rezervētu šo vietu. Spiediet 'Apstiprināt' zem šī paziņojuma.").format(svc['name'])
            )
            
            cursor.execute("""
                INSERT INTO waitlist_offers (waitlist_id, user_id, service_id, token, expires_at)
                VALUES (%s, %s, %s, %s, NOW() + INTERVAL '4 hours')
            """, [waitlist_id, user_id, service_id, token])

@csrf_exempt
def claim_waitlist_spot(request):
    if request.method != 'POST':
        return JsonResponse({"error": _("POST only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id = get_user_from_token(token)
    if not user_id:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    
    try:
        data = json.loads(request.body)
        waitlist_id = data.get('waitlist_id')
        service_id = data.get('service_id')
        date = data.get('date')
        time = data.get('time')
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT w.user_id, wo.token, wo.expires_at
                FROM waitlist_offers wo
                JOIN waitlist w ON w.id = wo.waitlist_id
                WHERE wo.waitlist_id = %s AND wo.service_id = %s AND NOW() < wo.expires_at
            """, [waitlist_id, service_id])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({"error": _("Šis piedāvājums ir beidzies vai nav derīgs.")}, status=400)
            if row[0] != user_id:
                return JsonResponse({"error": _("Unauthorized")}, status=401)
            
            svc = get_service(service_id)
            cursor.execute("""
                INSERT INTO reservations (user_id, service_name, res_date, res_time, provider_id, service_id, booked_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [user_id, svc['name'], date, time, svc['provider_id'], service_id, svc['price']])
            
            cursor.execute("UPDATE waitlist SET status = 'claimed' WHERE id = %s", [waitlist_id])
            
            cursor.execute("DELETE FROM waitlist_offers WHERE waitlist_id = %s", [waitlist_id])
        
        return JsonResponse({"status": "booking_created"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def check_admin(token):
    user_id = get_user_from_token(token)
    if not user_id:
        return None, False
    with connection.cursor() as cursor:
        cursor.execute("SELECT roles FROM auth_user WHERE id = %s", [user_id])
        row = cursor.fetchone()
        if not row or row[0] != 1:
            return user_id, False
        return user_id, True

@csrf_exempt
def admin_stats(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    user_id, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN roles = 1 THEN 1 ELSE 0 END) as admins,
                    SUM(CASE WHEN roles = 2 THEN 1 ELSE 0 END) as providers,
                    SUM(CASE WHEN roles = 3 THEN 1 ELSE 0 END) as clients
                FROM auth_user
            """)
            row = cursor.fetchone()
            stats = {
                "total_users": row[0],
                "admins": row[1] or 0,
                "providers": row[2] or 0,
                "clients": row[3] or 0,
            }
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'upcoming' THEN 1 ELSE 0 END) as upcoming,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                    COALESCE(SUM(booked_price), 0) as revenue
                FROM reservations
            """)
            row = cursor.fetchone()
            stats["total_bookings"] = row[0]
            stats["upcoming_bookings"] = row[1] or 0
            stats["completed_bookings"] = row[2] or 0
            stats["cancelled_bookings"] = row[3] or 0
            stats["total_revenue"] = float(row[4] or 0)
            
            cursor.execute("SELECT COUNT(*) FROM services")
            stats["total_services"] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT r.id, r.service_name, r.res_date, r.res_time, r.status,
                       u.username as client, p.username as provider, r.booked_price
                FROM reservations r
                JOIN auth_user u ON u.id = r.user_id
                JOIN auth_user p ON p.id = r.provider_id
                ORDER BY r.res_date DESC, r.res_time DESC
                LIMIT 10
            """)
            recent = []
            for row in cursor.fetchall():
                recent.append({
                    "id": row[0],
                    "service": row[1],
                    "date": str(row[2]),
                    "time": str(row[3])[:5] if row[3] else '',
                    "status": row[4],
                    "client": row[5],
                    "provider": row[6],
                    "price": float(row[7]) if row[7] else None,
                })
            stats["recent_bookings"] = recent
            
            cursor.execute("""
                SELECT 
                    TO_CHAR(DATE_TRUNC('month', res_date), 'YYYY-MM') as month,
                    COUNT(*) as count,
                    COALESCE(SUM(booked_price), 0) as revenue
                FROM reservations
                WHERE res_date >= NOW() - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', res_date)
                ORDER BY month ASC
            """)
            monthly = []
            for row in cursor.fetchall():
                monthly.append({
                    "month": row[0],
                    "count": row[1],
                    "revenue": float(row[2]),
                })
            stats["monthly_stats"] = monthly
            
            cursor.execute("""
                SELECT r.service_name, COUNT(*) as count, COALESCE(SUM(r.booked_price), 0) as revenue
                FROM reservations r
                GROUP BY r.service_name
                ORDER BY count DESC
                LIMIT 5
            """)
            top_services = []
            for row in cursor.fetchall():
                top_services.append({
                    "name": row[0],
                    "count": row[1],
                    "revenue": float(row[2]),
                })
            stats["top_services"] = top_services
            
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_get_users(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        role_filter = request.GET.get('role', '')
        with connection.cursor() as cursor:
            query = """
                SELECT id, username, email, roles, industry, description, 
                       phone, address, reg_number, is_active, date_joined
                FROM auth_user
            """
            params = []
            if role_filter and role_filter != 'all':
                query += " WHERE roles = %s"
                params.append(role_filter)
            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "roles": row[3],
                "industry": row[4] or '',
                "description": row[5] or '',
                "phone": row[6] or '',
                "address": row[7] or '',
                "reg_number": row[8] or '',
                "is_active": row[9],
                "date_joined": str(row[10])[:10] if row[10] else '',
            })
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_update_user(request, user_id):
    if request.method != 'PUT':
        return JsonResponse({"error": _("PUT only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE auth_user 
                SET username = %s, email = %s, roles = %s, industry = %s,
                    description = %s, phone = %s, address = %s, reg_number = %s,
                    is_active = %s
                WHERE id = %s
            """, [
                data.get('username'), data.get('email'), data.get('roles'),
                data.get('industry', ''), data.get('description', ''),
                data.get('phone', ''), data.get('address', ''),
                data.get('reg_number', ''), data.get('is_active', True),
                user_id
            ])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_delete_user(request, user_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": _("DELETE only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM auth_user WHERE id = %s", [user_id])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_get_services(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, s.name, s.price, s.description, s.duration_minutes,
                       s.work_days, s.work_start, s.work_end, s.provider_id,
                       u.username as provider_name
                FROM services s
                JOIN auth_user u ON u.id = s.provider_id
                ORDER BY s.id DESC
            """)
            rows = cursor.fetchall()
        
        services = []
        for row in rows:
            services.append({
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "description": row[3] or '',
                "duration_minutes": row[4] or 60,
                "work_days": row[5] or '1,2,3,4,5',
                "work_start": str(row[6])[:5] if row[6] else '09:00',
                "work_end": str(row[7])[:5] if row[7] else '17:00',
                "provider_id": row[8],
                "provider_name": row[9],
            })
        return JsonResponse(services, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_delete_service(request, service_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": _("DELETE only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM services WHERE id = %s", [service_id])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_get_bookings(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        status_filter = request.GET.get('status', '')
        with connection.cursor() as cursor:
            query = """
                SELECT r.id, r.service_name, r.res_date, r.res_time, r.res_end_time,
                       r.status, r.booked_price,
                       u.username as client, p.username as provider,
                       r.user_id, r.provider_id, r.service_id
                FROM reservations r
                JOIN auth_user u ON u.id = r.user_id
                JOIN auth_user p ON p.id = r.provider_id
            """
            params = []
            if status_filter and status_filter != 'all':
                query += " WHERE r.status = %s"
                params.append(status_filter)
            query += " ORDER BY r.res_date DESC, r.res_time DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        bookings = []
        for row in rows:
            bookings.append({
                "id": row[0],
                "service": row[1],
                "date": str(row[2]),
                "time": str(row[3])[:5] if row[3] else '',
                "end_time": str(row[4])[:5] if row[4] else '',
                "status": row[5] or 'upcoming',
                "price": float(row[6]) if row[6] else None,
                "client": row[7],
                "provider": row[8],
                "client_id": row[9],
                "provider_id": row[10],
                "service_id": row[11],
            })
        return JsonResponse(bookings, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_update_booking(request, booking_id):
    if request.method != 'PUT':
        return JsonResponse({"error": _("PUT only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        data = json.loads(request.body)
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE reservations 
                SET service_name = %s, res_date = %s, res_time = %s,
                    status = %s, booked_price = %s
                WHERE id = %s
            """, [
                data.get('service'), data.get('date'), data.get('time'),
                data.get('status'), data.get('price'), booking_id
            ])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def admin_delete_booking(request, booking_id):
    if request.method != 'DELETE':
        return JsonResponse({"error": _("DELETE only")}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({"error": _("Unauthorized")}, status=401)
    token = auth_header.split(' ')[1]
    _, is_admin = check_admin(token)
    if not is_admin:
        return JsonResponse({"error": _("Admin access required")}, status=403)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM reservations WHERE id = %s", [booking_id])
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)