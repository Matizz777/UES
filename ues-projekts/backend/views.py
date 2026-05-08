from django.http import JsonResponse
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.db import connection, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
import json
import uuid
from datetime import datetime, timedelta

@csrf_exempt
def get_user_reservations(request):
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]

        with connection.cursor() as cursor:
            # Atrodam lietotāju
            cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [token])
            user = cursor.fetchone()
            
            if not user:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # Atlasām rezervācijas
            cursor.execute("""
                SELECT id, service_name, res_date, res_time 
                FROM reservations 
                WHERE user_id = %s 
                ORDER BY res_date ASC, res_time ASC
            """, [user[0]])
            
            rows = cursor.fetchall()
            
            # Debug - izvadām, ko atgriež datubāze
            print(f"DB atgrieztie dati: {rows}")
            
            res_list = []
            for r in rows:
                # Apstrādājam laiku
                time_value = r[3]
                if time_value:
                    # Ja ir datetime.time objekts
                    if hasattr(time_value, 'strftime'):
                        time_str = time_value.strftime("%H:%M")
                    else:
                        # Ja ir string
                        time_str = str(time_value)[:5]
                else:
                    time_str = "Nav laika"
                
                res_list.append({
                    "id": r[0], 
                    "service": r[1], 
                    "date": str(r[2]), 
                    "time": time_str
                })
            
            print(f"Atgriežamais saraksts: {res_list}")  # Debug
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
            # 1. Pārbaudām autorizāciju (tokenu)
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JsonResponse({"error": "Nav autorizācijas"}, status=401)
            
            token = auth_header.split(' ')[1]
            data = json.loads(request.body)
            
            print(f"Saņemtie dati: {data}")  # Debug
            
            with connection.cursor() as cursor:
                # 2. Atrodam lietotāju pēc tokena
                cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [token])
                user = cursor.fetchone()
                
                if not user:
                    return JsonResponse({"error": "Sesija nederīga"}, status=401)

                user_id = user[0]
                service = data.get('service') or data.get('service_name')  # Atbalsta abus variantus
                date = data.get('date') or data.get('res_date')
                time = data.get('time') or data.get('res_time')
                
                print(f"Saglabājam: user_id={user_id}, service={service}, date={date}, time={time}")  # Debug

                # 3. Pārliecināmies, ka laiks ir pareizā formātā
                if time and ':' in time:
                    # Ja laiks ir "14:00", pievienojam sekundes
                    if time.count(':') == 1:
                        time = f"{time}:00"
                
                # 4. Ierakstām rezervāciju datubāzē
                cursor.execute(
                    """
                    INSERT INTO reservations (user_id, service_name, res_date, res_time)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [user_id, service, date, time]
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
                # Atlasām visus laikus šim datumam
                cursor.execute("SELECT res_time FROM reservations WHERE res_date = %s", [date_str])
                rows = cursor.fetchall()
                
                # Pārveidojam no SQL formāta (10:00:00) uz (10:00)
                # str(r[0])[:5] paņem pirmos 5 simbolus no laika
                occupied = [r[0].strftime("%H:%M") if hasattr(r[0], 'strftime') else str(r[0])[:5] for r in rows]
            return JsonResponse(occupied, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def cancel_booking(request, booking_id):  # booking_id šeit ir obligāts!
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                # Pārbaudām, vai eksistē
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
        # 1. Dabūjam speciālistus
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
        # 2. Ejam cauri speciālistiem, izmantojot to pašu kursoru
        for row in providers_rows:
            p_id = row[0]
            
            # Izpildām vaicājumu pakalpojumiem
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
                "services": p_services  # Šeit jau ir pareizi!
            })

    return JsonResponse(result, safe=False)

@csrf_exempt
def add_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_token = request.headers.get('Authorization').split(' ')[1]
        
        with connection.cursor() as cursor:
            # Atrodam sniedzēja ID pēc tokena
            cursor.execute("SELECT id FROM auth_user WHERE session_token = %s", [user_token])
            provider_id = cursor.fetchone()[0]
            
            # Ieliekam jaunu brīvo laiku
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
    slot_duration = 30 # minūtes
    
    slots = []
    current_time = datetime.strptime(f"{date_str} {start_hour}:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(f"{date_str} {end_hour}:00", "%Y-%m-%d %H:%M")

    # 2. Atrodam jau aizņemtos laikus no datubāzes
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
            print(f"KĻŪDA SERVERĪ: {e}") # ŠIS IZDRUKĀS ĪSTO VAINU
            return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            # Izveidojam unikālu tokenu šai sesijai
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
                        data.get('password'), 
                        data.get('roles', 3), 
                        data.get('industry', ''), 
                        data.get('description', ''),
                        '', # first_name
                        '', # last_name
                        True, # is_active
                        datetime.now(),
                        token # ŠIS SAGLABĀ TOKENU DB, LAI 401 PAZUSTU
                    ]
                )
                new_id = cursor.fetchone()[0]

            return JsonResponse({
                "id": new_id, 
                "username": username, 
                "roles": data.get('roles'), 
                "token": token # Sūtam to pašu tokenu uz Vue
            }, status=201)
        except Exception as e:
            # Šis izvadīs terminālī precīzu kļūdu, ja atkal nesakritīs kolonnas
            print(f"DB ERROR: {e}") 
            return JsonResponse({"error": str(e)}, status=500)