# API VIEWS - Vues pour l'API REST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from ..permissions import IsAdmin, IsRecruteurOrAdmin
from ..serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserListSerializer
)
from ..models import User


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


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur via API"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Connexion utilisateur via API"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Connexion réussie',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Profil de l'utilisateur connecté via API"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Modifier son profil via API"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour',
            'user': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsRecruteurOrAdmin])
def list_users(request):
    """Liste des utilisateurs (recruteurs et admins seulement) via API"""
    users = User.objects.all().order_by('-created_at')
    
    # Filtrer par rôle si demandé
    role = request.query_params.get('role')
    if role:
        users = users.filter(role=role)
    
    serializer = UserListSerializer(users, many=True)
    return Response({
        'count': users.count(),
        'users': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_info(request):
    """Voir les infos de l'utilisateur connecté (pour tests) via API"""
    return Response({
        'email': request.user.email,
        'role': request.user.role,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'groups': [g.name for g in request.user.groups.all()]
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_only(request):
    """Endpoint que seuls les admins peuvent voir via API"""
    return Response({
        'message': 'Tu es admin !',
        'secret': 'Seuls les admins voient ce message'
    })
