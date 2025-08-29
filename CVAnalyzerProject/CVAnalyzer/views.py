# TISMA IMPORT
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# import json

# IMPORTS POUR L'API REST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# IMPORTS DJANGO POUR LES VUES TEMPLATES (si on en a besoin)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# IMPORTS LOCAUX
from .permissions import IsAdmin, IsRecruteurOrAdmin
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserListSerializer,
    CandidatureCreateSerializer,
    CandidatureListSerializer,
    CandidatureUpdateSerializer
)
from .models import User, Candidature


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
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
    """Connexion utilisateur"""
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
    """Profil de l'utilisateur connecté"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Modifier son profil"""
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
    """Liste des utilisateurs (recruteurs et admins seulement)"""
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
    """Voir les infos de l'utilisateur connecté (pour tests)"""
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
    """Endpoint que seuls les admins peuvent voir"""
    return Response({
        'message': 'Tu es admin !',
        'secret': 'Seuls les admins voient ce message'
    })


#  VUES CANDIDATURES

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidature(request):
    """Créer une nouvelle candidature (candidats seulement)"""
    # Vérifier que l'utilisateur est un candidat
    if request.user.role != 'candidat':
        return Response({
            'error': 'Seuls les candidats peuvent créer des candidatures'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CandidatureCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        candidature = serializer.save()
        
        # Retourner la candidature créée avec tous les détails
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
        # Les candidats voient seulement leurs candidatures
        candidatures = Candidature.objects.filter(candidat=user)
    elif user.role in ['recruteur', 'admin']:
        # Les recruteurs et admins voient toutes les candidatures
        candidatures = Candidature.objects.all()
        
        # Filtres optionnels
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
    
    # Vérification des permissions
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
    
    # Seuls les recruteurs/admins peuvent modifier le statut
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
        
        # Retourner la candidature mise à jour
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
    
    # Les candidats peuvent supprimer leurs candidatures, les admins toutes
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


def home(request):
    context = {
        # titre de la page
        'title': 'Candidatures - Dépôt de CV',
    }
    return render(request, 'pages/home.html', context)

# page login
def login_view(request):
    # methode http
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # user par mail
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'ggwp')
                return redirect('home')
            else:
                messages.error(request, 'mail ou mot de passe incorrect.')
        except User.DoesNotExist:
            messages.error(request, 'aucun compte trouvé avec cette adresse email.')
    
    return render(request, 'pages/login.html')

# page inscription
def register_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # validation (le blabla habituel)
        if password1 != password2:
            messages.error(request, 'Mots de passe ne correspondent pas.')
            return render(request, 'pages/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Adresse email est déjà utilisée.')
            return render(request, 'pages/register.html')
        
        # nom d'utilisateur basé sur le prénom
        username_base = first_name.replace(' ', '')
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        # création du compte
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Votre compte a été créé')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Erreur lors de la création du compte.')
    
    return render(request, 'pages/register.html')

# déco
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('home')

@login_required
def upload_documents(request):
    if request.method == 'POST':
        # upload des fichiers on verra plus tard
        return JsonResponse({
            'success': True,
            'message': 'Documents reçus et en cours d\'analyse par notre IA.'
        })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

# check si le user est co
def check_auth_status(request):
    if request.user.is_authenticated:
        # nom d'affichage (prénom + nom ou email si pas de nom (n'arrivera jamais))
        display_name = f"{request.user.first_name} {request.user.last_name}".strip()
        if not display_name:
            display_name = request.user.email
    else:
        display_name = None
    
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'display_name': display_name
    })