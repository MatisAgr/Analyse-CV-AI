from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import views

@api_view(['GET'])
def api_status(request):
    """Endpoint temporaire pour vérifier que l'API fonctionne"""
    return Response({
        'status': 'API CVAnalyzer - Étape 1 configurée',
        'version': '1.0.0',
        'message': 'Configuration de base terminée'
    })

urlpatterns = [
    # API endpoints
    path('status/', api_status, name='api-status'),
    path('api/auth-status/', views.check_auth_status, name='auth-status'),
    path('api/upload/', views.upload_documents, name='upload-documents'),

    # Vues Django
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
