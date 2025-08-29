from django.urls import path
from .views import api_views  # Import des vues API
from .views import template_views  # Import des vues templates
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import security_views

@api_view(['GET'])
# petit check up pour voir si l'api marche
def api_status(request):
    return Response({
        'status': 'API CVAnalyzer',
        'version': '3.0.0',
        'message': 'Endpoints API DRF prêts',
        'endpoints': [
            'POST /api/register/',
            'POST /api/login/',
            'GET /api/users/me/',
            'PUT /api/users/me/',
            'GET /api/users/',
            'POST /api/candidatures/',
            'GET /api/candidatures/',
            'GET /api/candidatures/{id}/',
            'PUT /api/candidatures/{id}/',
            'DELETE /api/candidatures/{id}/',
            'GET /api/security/status/',
            'GET /api/security/csrf-token/',
            'POST /api/security/test-xss/',
            'GET /api/security/user-info/',
        ]
    })

urlpatterns = [
    # API ENDPOINTS (REST)    

    # Status API
    path('status/', api_views.api_status, name='api-status'),
    
    # Authentification API
    path('api/register/', api_views.register, name='api-register'),
    path('api/login/', api_views.login_user, name='api-login'),
    
    # Profil utilisateur API
    path('api/users/me/', api_views.user_profile, name='user-profile'),
    path('api/users/me/update/', api_views.update_profile, name='update-profile'),
    
    # Gestion utilisateurs API (admin/recruteur)
    path('api/users/', api_views.list_users, name='list-users'),
    
    # Tests API
    path('api/check/', api_views.check_user_info, name='check-user'),
    path('api/admin-only/', api_views.admin_only, name='admin-only'),
  
    # Tests
    path('check/', views.check_user_info, name='check-user'),
    path('admin-only/', views.admin_only, name='admin-only'),
    
    # Candidatures
    path('candidatures/', views.list_candidatures, name='list-candidatures'),
    path('candidatures/create/', views.create_candidature, name='create-candidature'),
    path('candidatures/<int:candidature_id>/', views.get_candidature, name='get-candidature'),
    path('candidatures/<int:candidature_id>/update/', views.update_candidature, name='update-candidature'),
    path('candidatures/<int:candidature_id>/delete/', views.delete_candidature, name='delete-candidature'),
    
    # Sécurité 
    path('security/status/', security_views.security_status, name='security-status'),
    path('security/csrf-token/', security_views.get_csrf_token, name='csrf-token'),
    path('security/test-xss/', security_views.test_xss_protection, name='test-xss'),
    path('security/user-info/', security_views.user_security_info, name='user-security'),
  
    
    # ================================================================================================
    # TEMPLATE VIEWS (HTML Pages)
    
    # pages principales
    path('', template_views.home, name='home'),
    path('login/', template_views.login_view, name='login'),
    path('register/', template_views.register_view, name='register'),
    path('logout/', template_views.logout_view, name='logout'),
    
    # Fonctionnalités
    path('upload/', template_views.upload_documents, name='upload-documents'),
    path('auth-status/', template_views.check_auth_status, name='auth-status'),

]
