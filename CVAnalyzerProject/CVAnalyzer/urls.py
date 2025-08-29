from django.urls import path
from .views import api_views  # Import des vues API
from .views import template_views  # Import des vues templates
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import security_views

@api_view(['GET'])
def api_status(request):
    """Endpoint temporaire pour vérifier que l'API fonctionne"""
    return Response({
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
    # ================================================================================================
    # API ENDPOINTS (REST)    

    # Status API
    path('api/status/', api_status, name='api-status'),
    
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
    
    # Candidatures API
    path('api/candidatures/', api_views.list_candidatures, name='list-candidatures'),
    path('api/candidatures/create/', api_views.create_candidature, name='create-candidature'),
    path('api/candidatures/<int:candidature_id>/', api_views.get_candidature, name='get-candidature'),
    path('api/candidatures/<int:candidature_id>/update/', api_views.update_candidature, name='update-candidature'),
    path('api/candidatures/<int:candidature_id>/delete/', api_views.delete_candidature, name='delete-candidature'),
    
    # Sécurité API
    path('api/security/status/', security_views.security_status, name='security-status'),
    path('api/security/csrf-token/', security_views.get_csrf_token, name='csrf-token'),
    path('api/security/test-xss/', security_views.test_xss_protection, name='test-xss'),
    path('api/security/user-info/', security_views.user_security_info, name='user-security'),
    
    # ================================================================================================
    # TEMPLATE VIEWS (HTML Pages)
    
    # Pages principales
    path('', template_views.home, name='home'),
    path('login/', template_views.login_view, name='login'),
    path('register/', template_views.register_view, name='register'),
    path('logout/', template_views.logout_view, name='logout'),
    path('account/', template_views.account_view, name='account'),
    path('account/<int:candidature_id>/', template_views.candidature_detail_view, name='candidature-detail'),
    
    # dashboard recruteur
    path('recruiter/', template_views.recruiter_dashboard_view, name='recruiter-dashboard'),
    
    # Fonctionnalités
    path('upload/', template_views.upload_documents, name='upload-documents'),
    path('auth-status/', template_views.check_auth_status, name='auth-status'),
]
