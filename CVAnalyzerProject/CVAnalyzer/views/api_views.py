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
    UserListSerializer,
    CandidatureCreateSerializer,
    CandidatureListSerializer,
    CandidatureUpdateSerializer
)
from ..models import User, Candidature


# endpoint de vérification de l'état de l'API
@api_view(['GET'])
def api_status(request):
    return Response({
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


# inscription utilisateur
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
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


#connexion
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # générer les tokens JWT
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


# profil de l'utilisateur connecté
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


# modification du profil
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil mis à jour',
            'user': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# liste des utilisateurs
@api_view(['GET'])
@permission_classes([IsRecruteurOrAdmin])
def list_users(request):
    users = User.objects.all().order_by('-created_at')
    
    # filtrer par rôle si demandé
    role = request.query_params.get('role')
    if role:
        users = users.filter(role=role)
    
    serializer = UserListSerializer(users, many=True)
    return Response({
        'count': users.count(),
        'users': serializer.data
    })


# vérification des informations de l'utilisateur
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_info(request):
    return Response({
        'email': request.user.email,
        'role': request.user.role,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'groups': [g.name for g in request.user.groups.all()]
    })


# vérification si admin
@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_only(request):
    return Response({
        'message': 'Tu es admin !',
        'secret': 'Seuls les admins voient ce message'
    })


# postuler ici
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidature(request):
    # vérifier que l'utilisateur est un candidat
    if request.user.role != 'candidat':
        return Response({
            'error': 'Seuls les candidats peuvent créer des candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CandidatureCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        candidature = serializer.save()
        
        # retourner la candidature créée
        response_serializer = CandidatureListSerializer(candidature, context={'request': request})
        return Response({
            'message': 'Candidature créée avec succès',
            'candidature': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_candidatures(request):
    """Lister les candidatures selon le rôle"""
    user = request.user
    
    if user.role == 'candidat':
        candidatures = Candidature.objects.filter(candidat=user)
    elif user.role in ['recruteur', 'admin']: # les recruteurs et admins voient toutes les candidatures
        candidatures = Candidature.objects.all()
     
        status_filter = request.query_params.get('status')
        if status_filter:
            candidatures = candidatures.filter(status=status_filter)
            
        poste_filter = request.query_params.get('poste')
        if poste_filter:
            candidatures = candidatures.filter(poste__icontains=poste_filter)
    else:
        return Response({
            'error': 'Accès non autorisé'
        }, status=status.HTTP_403_FORBIDDEN)
    
    candidatures = candidatures.order_by('-created_at')
    serializer = CandidatureListSerializer(candidatures, many=True, context={'request': request})
    
    return Response({
        'count': candidatures.count(),
        'candidatures': serializer.data
    })
  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_candidature(request, candidature_id):
    """Voir une candidature spécifique"""
    try:
        candidature = Candidature.objects.get(id=candidature_id)
    except Candidature.DoesNotExist:
        return Response({
            'error': 'Candidature non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # vérification des permissions
    user = request.user
    if user.role == 'candidat' and candidature.candidat != user:
        return Response({
            'error': 'Vous ne pouvez voir que vos propres candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CandidatureListSerializer(candidature, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_candidature(request, candidature_id):
    """Modifier une candidature (statut par les recruteurs)"""
    try:
        candidature = Candidature.objects.get(id=candidature_id)
    except Candidature.DoesNotExist:
        return Response({
            'error': 'Candidature non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # seuls les recruteurs/admins peuvent modifier le statut
    if request.user.role not in ['recruteur', 'admin']:
        return Response({
            'error': 'Seuls les recruteurs peuvent modifier les candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CandidatureUpdateSerializer(
        candidature, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        candidature = serializer.save()
        
        response_serializer = CandidatureListSerializer(candidature, context={'request': request})
        return Response({
            'message': 'Candidature mise à jour',
            'candidature': response_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_candidature(request, candidature_id):
    """Supprimer une candidature"""
    try:
        candidature = Candidature.objects.get(id=candidature_id)
    except Candidature.DoesNotExist:
        return Response({
            'error': 'Candidature non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # les candidats peuvent supprimer leurs candidatures
    if request.user.role == 'candidat' and candidature.candidat != request.user:
        return Response({
            'error': 'Vous ne pouvez supprimer que vos propres candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'recruteur':
        return Response({
            'error': 'Les recruteurs ne peuvent pas supprimer les candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    
    candidature.delete()
    return Response({
        'message': 'Candidature supprimée avec succès'
    }, status=status.HTTP_204_NO_CONTENT)