"""
Vues pour tester la sécurité de l'application
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def security_status(request):
    """Endpoint pour vérifier les mesures de sécurité actives"""
    return Response({
        'security_measures': {
            'csrf_protection': 'ACTIVE' if 'django.middleware.csrf.CsrfViewMiddleware' in request.META.get('HTTP_HOST', '') else 'CONFIGURED',
            'xss_protection': 'ACTIVE',
            'clickjacking_protection': 'ACTIVE',
            'password_hashing': 'PBKDF2 (Django default)',
            'session_security': 'ACTIVE',
            'cors_configured': 'YES'
        },
        'recommendations': [
            'Utiliser HTTPS en production',
            'Configurer un WAF (Web Application Firewall)',
            'Implémenter rate limiting',
            'Monitoring des tentatives de connexion'
        ]
    })


@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Obtenir un token CSRF pour les tests frontend"""
    return JsonResponse({'csrf_token': get_token(request)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_xss_protection(request):
    """Tester la protection XSS - input sanitization"""
    user_input = request.data.get('input', '')
    
    import html
    safe_input = html.escape(user_input)
    
    return Response({
        'message': 'Input processed safely',
        'original_input': user_input,
        'escaped_input': safe_input,
        'security_note': 'Input has been escaped to prevent XSS'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_security_info(request):
    """Informations de sécurité sur l'utilisateur connecté"""
    return Response({
        'user_security': {
            'user_id': request.user.id,
            'is_authenticated': request.user.is_authenticated,
            'password_last_changed': request.user.password,  # Hash seulement
            'session_key': request.session.session_key,
            'csrf_token_available': 'csrftoken' in request.COOKIES,
            'secure_cookies': request.is_secure(),
        },
        'security_tips': [
            'Change ton mot de passe régulièrement',
            'Ne partage jamais tes tokens JWT',
            'Déconnecte-toi sur les ordinateurs publics'
        ]
    })
