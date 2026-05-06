from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.db import connection, IntegrityError
import json
import uuid

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = make_password(data.get('password'))
            role = int(data.get('roles', 3))
            
            session_token = str(uuid.uuid4()) 

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auth_user (
                        username, email, password, roles, 
                        is_active, date_joined, first_name, last_name,
                        session_token
                    )
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s)
                    """,
                    [username, email, password, role, True, '', '', session_token]
                )

            return JsonResponse({
                "token": session_token,
                "username": username,
                "roles": role
            }, status=201)
            
        except IntegrityError:
            return JsonResponse({"error": "Lietotājvārds jau ir aizņemts!"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"status": "Online"}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user, name='register'),
]