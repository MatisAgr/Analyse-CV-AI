from django.urls import path
from .views import api_views  # Import des vues API
from .views import template_views  # Import des vues templates

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
    
    # ================================================================================================
    # TEMPLATE VIEWS (HTML Pages)
    
    # Pages principales
    path('', template_views.home, name='home'),
    path('login/', template_views.login_view, name='login'),
    path('register/', template_views.register_view, name='register'),
    path('logout/', template_views.logout_view, name='logout'),
    
    # Fonctionnalités
    path('upload/', template_views.upload_documents, name='upload-documents'),
    path('auth-status/', template_views.check_auth_status, name='auth-status'),
]
