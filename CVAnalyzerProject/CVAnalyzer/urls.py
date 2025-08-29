from django.urls import path

from .views import api_views        # Import des vues API
from .views import template_views   # Import des vues templates
from .views import security_views   # Import des vues sécurité
# from .views import ai_views         # Import des vues IA - temporairement désactivé

from rest_framework.response import Response
from rest_framework.decorators import api_view

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
    
    # Actions candidatures (recruteur)
    path('candidature/<int:candidature_id>/accepter/', template_views.accepter_candidature, name='accepter-candidature'),
    path('candidature/<int:candidature_id>/refuser/', template_views.refuser_candidature, name='refuser-candidature'),
    path('candidature/<int:candidature_id>/changer-statut/', template_views.changer_statut_candidature, name='changer-statut-candidature'),
    
    # Fonctionnalités
    path('upload/', template_views.upload_documents, name='upload-documents'),
    path('auth-status/', template_views.check_auth_status, name='auth-status'),
    
    # ================================================================================================
    # IA VIEWS - Temporairement désactivées à cause des dépendances manquantes
    
    # Documentation API (temporairement désactivée)
    # path('api/', ai_views.api_index, name='api_index'),

    # API endpoints temporairement commentées en attendant l'implémentation
    # path('api/upload-cv/', ai_views.upload_cv, name='upload_cv'),
    # path('api/analyze-cv-job/', ai_views.analyze_cv_for_job, name='analyze_cv_for_job'),
    # path('api/resume/<int:resume_id>/', ai_views.get_resume_details, name='resume_details'),
    # path('api/resumes/', ai_views.list_resumes, name='list_resumes'),
    # path('api/download-dataset/', ai_views.download_dataset, name='download_dataset'),
    # path('api/ai-status/', ai_views.ai_status, name='ai_status'),
    
    # AI Training API - temporairement commentées
    # path('api/train-model/', ai_views.train_ai_model, name='train_model'),
    # path('api/predict-category/', ai_views.predict_cv_category, name='predict_category'),
    # path('api/score-cv-job/', ai_views.score_cv_job_match, name='score_cv_job'),
    # path('api/model-metrics/', ai_views.get_model_metrics, name='model_metrics'),
]
