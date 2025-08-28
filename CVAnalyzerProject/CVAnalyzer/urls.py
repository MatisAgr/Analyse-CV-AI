from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import views

@api_view(['GET'])
def api_status(request):
    """Endpoint temporaire pour vérifier que l'API fonctionne"""
    return Response({
        'status': 'API CVAnalyzer - Étape 3 terminée',
        'version': '3.0.0',
        'message': 'Endpoints API DRF prêts',
        'endpoints': [
            'POST /api/register/',
            'POST /api/login/',
            'GET /api/users/me/',
            'PUT /api/users/me/',
            'GET /api/users/',
            'GET /api/check/',
            'GET /api/admin-only/'
        ]
    })

urlpatterns = [
    # Status
    path('status/', api_status, name='api-status'),
    
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    
    # Profil utilisateur
    path('users/me/', views.user_profile, name='user-profile'),
    path('users/me/update/', views.update_profile, name='update-profile'),
    
    # Gestion utilisateurs (admin/recruteur)
    path('users/', views.list_users, name='list-users'),
    
    # Tests
    path('check/', views.check_user_info, name='check-user'),
    path('admin-only/', views.admin_only, name='admin-only'),
  
  
    # Vues Django
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
