# UES — File Structure

```
src/
├── App.vue                         # Root: auth state, login/register/dashboard routing
├── assets/
│   └── style.css                   # (unchanged — copy your existing file here)
└── components/
    ├── NavBar.vue                  # Top navigation bar (logo + user info/logout)
    ├── LoginForm.vue               # Login card (new — calls POST /api/login/)
    ├── RegisterForm.vue            # Registration card
    ├── Dashboard.vue               # Shell: picks ProviderDashboard or ClientDashboard
    ├── ProviderDashboard.vue       # Add service + availability calendar (role=2)
    ├── ClientDashboard.vue         # Catalog + booking flow (role=3)
    ├── ProviderCatalog.vue         # Search/filter grid + provider profile overlay
    ├── BookingWizard.vue           # Date → time → confirm wizard
    └── ReservationList.vue         # Shared reservation list (cancel works for both roles)
```

## What changed

### New: LoginForm.vue
- Calls `POST /api/login/` with `{ username, password }`
- Expects the same `{ token, roles, username, id, … }` shape as register
- Shows inline error messages instead of `alert()`

### Auth flow in App.vue
- Landing page now shows two buttons: **Pieslēgties** and **Reģistrēties**
- `authView` ref controls which card is shown (`'none'` | `'login'` | `'register'`)
- Both forms emit `login-success` / `register-success` → `onAuthSuccess()` in App.vue

### Bug fixes carried over from refactor
| Bug | Fix |
|---|---|
| `selectedProvider` was declared as both a `ref` and a function | Removed the duplicate function; `selectedProvider` is a `ref` only |
| `bookingData.value.date` vs `bookingData.date` mismatch | `bookingData` is `reactive`, so always accessed without `.value` |
| `isSelected` tried `bookingData.value.date` | Fixed to use plain `selectedDate` ref inside `BookingWizard` |
| `ReservationList` wasn't loaded on tab switch | `onMounted` handles initial load; component is re-mounted on tab switch |

## Backend requirement for login
Your Django backend needs a login endpoint, e.g.:

```python
# urls.py
path('api/login/', views.login_view),

# views.py
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def login_view(request):
    data = json.loads(request.body)
    user = authenticate(username=data['username'], password=data['password'])
    if not user:
        return JsonResponse({'error': 'Nepareizs lietotājvārds vai parole.'}, status=400)
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        'token': str(refresh.access_token),
        'id': user.id,
        'username': user.username,
        'roles': user.profile.roles,   # adjust to your model
    })
```
