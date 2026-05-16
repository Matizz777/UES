from django.http import JsonResponse
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection, IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from datetime import datetime, timedelta

@csrf_exempt
def get_user_reservations(request):
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        role = request.GET.get('role', '3')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [token])
            user = cursor.fetchone()

            if not user:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            user_id = user[0]

            if role == '2':  # operator — fetch bookings made TO them
                cursor.execute("""
                    SELECT r.id, r.service_name, r.res_date, r.res_time, u.username as client_name
                    FROM reservations r
                    JOIN auth_user u ON u.id = r.user_id
                    WHERE r.provider_id = %s
                    ORDER BY r.res_date ASC, r.res_time ASC
                """, [user_id])
            else:  # client — fetch their own bookings
                cursor.execute("""
                    SELECT r.id, r.service_name, r.res_date, r.res_time, '' as client_name
                    FROM reservations r
                    WHERE r.user_id = %s
                    ORDER BY r.res_date ASC, r.res_time ASC
                """, [user_id])

            rows = cursor.fetchall()
            res_list = []
            for r in rows:
                time_value = r[3]
                time_str = time_value.strftime("%H:%M") if hasattr(time_value, 'strftime') else str(time_value)[:5]
                res_list.append({
                    "id": r[0],
                    "service": r[1],
                    "date": str(r[2]),
                    "time": time_str,
                    "client_name": r[4]
                })

            return JsonResponse(res_list, safe=False)

    except Exception as e:
        print(f"Kļūda get_user_reservations: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def save_booking(request):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({"error": "Nav autorizācijas"}, status=401)

            token = auth_header.split(' ')[1]
            data = json.loads(request.body)

            print(f"Saņemtie dati: {data}")

            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [token])
                user = cursor.fetchone()

                if not user:
                    return JsonResponse({"error": "Sesija nederīga"}, status=401)

                user_id = user[0]
                service = data.get('service') or data.get('service_name')
                date = data.get('date') or data.get('res_date')
                time = data.get('time') or data.get('res_time')
                provider_id = data.get('provider_id')

                print(f"Saglabājam: user_id={user_id}, service={service}, date={date}, time={time}, provider_id={provider_id}")

                if time and ':' in time:
                    if time.count(':') == 1:
                        time = f"{time}:00"

                cursor.execute(
                    """
                    INSERT INTO reservations (user_id, service_name, res_date, res_time, provider_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [user_id, service, date, time, provider_id]
                )

            return JsonResponse({"message": "Rezervācija saglabāta!"}, status=201)

        except Exception as e:
            print(f"Kļūda: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Tikai POST pieprasījumi"}, status=405)

@csrf_exempt
def get_occupied_times(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse([], safe=False)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT res_time FROM reservations WHERE res_date = %s", [date_str])
                rows = cursor.fetchall()

                occupied = [r[0].strftime("%H:%M") if hasattr(r[0], 'strftime') else str(r[0])[:5] for r in rows]
            return JsonResponse(occupied, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def cancel_booking(request, booking_id):
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM reservations WHERE id = %s", [booking_id])
                return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def get_providers(request):
    search = request.GET.get('search', '')
    industry = request.GET.get('industry', '')

    with connection.cursor() as cursor:
        query = "SELECT id, username, industry, description FROM auth_user WHERE roles = 2"
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

            cursor.execute("SELECT id, name, price FROM services WHERE provider_id = %s", [p_id])
            s_rows = cursor.fetchall()

            p_services = [
                {"id": s[0], "name": s[1], "price": float(s[2])}
                for s in s_rows
            ]

            result.append({
                "id": p_id,
                "username": row[1],
                "industry": row[2] or 'Nav norādīta',
                "description": row[3] or 'Nav apraksta.',
                "services": p_services
            })

    return JsonResponse(result, safe=False)

@csrf_exempt
def add_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_token = request.headers.get('Authorization').split(' ')[1]

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [user_token])
            provider_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO provider_availability (provider_id, available_date, available_time) VALUES (%s, %s, %s)",
                [provider_id, data['date'], data['time']]
            )
        return JsonResponse({"status": "Pievienots!"})

@csrf_exempt
def set_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        return JsonResponse({"status": "success"})

def get_available_slots(request):
    provider_id = request.GET.get('provider_id')
    date_str = request.GET.get('date')

    start_hour = 9
    end_hour = 17
    slot_duration = 30  # minūtes

    slots = []
    current_time = datetime.strptime(f"{date_str} {start_hour}:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(f"{date_str} {end_hour}:00", "%Y-%m-%d %H:%M")

    with connection.cursor() as cursor:
        cursor.execute("SELECT time FROM reservations WHERE provider_id = %s AND date = %s", [provider_id, date_str])
        occupied = [str(r[0])[:5] for r in cursor.fetchall()]

    while current_time < end_time:
        time_str = current_time.strftime("%H:%M")
        if time_str not in occupied:
            slots.append(time_str)
        current_time += timedelta(minutes=slot_duration)

    return JsonResponse(slots, safe=False)

@csrf_exempt
def add_service(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Saņemtie dati: {data}")

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO services (name, price, provider_id) VALUES (%s, %s, %s)",
                    [data.get('name'), data.get('price'), data.get('provider_id')]
                )
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            print(f"KĻŪDA SERVERĪ: {e}")
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            token = f"token-{username}"

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auth_user 
                    (username, email, password, roles, industry, description, first_name, last_name, is_active, date_joined, session_token) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    RETURNING id
                    """,
                    [
                        username,
                        data.get('email'),
                        make_password(data.get('password')),
                        data.get('roles', 3),
                        data.get('industry', ''),
                        data.get('description', ''),
                        '',  # first_name
                        '',  # last_name
                        True,  # is_active
                        datetime.now(),
                        token
                    ]
                )
                new_id = cursor.fetchone()[0]

            return JsonResponse({
                "id": new_id,
                "username": username,
                "roles": data.get('roles'),
                "token": token
            }, status=201)
        except Exception as e:
            print(f"DB ERROR: {e}")
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password, roles, session_token FROM auth_user WHERE username = %s",
                    [username]
                )
                user = cursor.fetchone()

            if not user:
                return JsonResponse({"error": "Nepareizs lietotājvārds vai parole."}, status=400)

            if not check_password(password, user[2]):
                return JsonResponse({"error": "Nepareizs lietotājvārds vai parole."}, status=400)

            return JsonResponse({
                "id": user[0],
                "username": user[1],
                "roles": user[3],
                "token": user[4]
            })

        except Exception as e:
            print(f"Login kļūda: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Tikai POST pieprasījumi"}, status=405)