from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_status(request):
    """Endpoint temporaire pour vérifier que l'API fonctionne"""
    return Response({
        'status': 'API CVAnalyser - Étape 1 configurée',
        'version': '1.0.0',
        'message': 'Configuration de base terminée'
    })

urlpatterns = [
    path('status/', api_status, name='api-status'),
]
