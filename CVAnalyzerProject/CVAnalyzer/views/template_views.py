# TEMPLATE VIEWS - Vues pour les templates HTML
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import models
import os
import json

# Import des services IA
from ..ai_services.text_extractor import TextExtractor
from ..ai_services.cv_analyzer import CVAnalyzer
from ..models import Candidature

# Utiliser le modèle User personnalisé
User = get_user_model()


# page home
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
        
        # authentification directe avec email (grâce à USERNAME_FIELD = 'email')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect('home')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    
    return render(request, 'pages/login.html')

# page inscription
def register_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
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
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
            return render(request, 'pages/register.html')

        # création du compte avec le username fourni
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Votre compte a été créé avec succès !')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du compte: {str(e)}')
    
    return render(request, 'pages/register.html')

# déco
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('home')

@login_required
def upload_documents(request):
    """
    Vue pour gérer l'upload de CV et l'analyse IA
    """
    if request.method == 'POST':
        try:
            # Vérification qu'un fichier CV est présent
            if 'cv' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'Aucun fichier CV trouvé.'
                })
            
            cv_file = request.FILES['cv']
            
            # Validation du type de fichier
            allowed_extensions = ['pdf', 'doc', 'docx']
            file_extension = cv_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'message': 'Format de fichier non supporté. Utilisez PDF, DOC ou DOCX.'
                })
            
            # Sauvegarde temporaire du fichier
            file_path = default_storage.save(f'temp_cv/{cv_file.name}', ContentFile(cv_file.read()))
            full_file_path = os.path.join(default_storage.location, file_path)
            
            # Extraction du texte
            extractor = TextExtractor()
            
            if file_extension == 'pdf':
                extraction_result = extractor.extract_from_pdf(full_file_path)
            else:  # doc/docx
                extraction_result = extractor.extract_from_docx(full_file_path)
            
            if not extraction_result['success']:
                # Nettoyage du fichier temporaire
                if os.path.exists(full_file_path):
                    os.remove(full_file_path)
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de l\'extraction du texte: {extraction_result["error"]}'
                })
            
            extracted_text = extraction_result['text']
            
            # Analyse IA du CV avec optimisations GPU
            analyzer = CVAnalyzer()
            
            # Affichage des informations GPU
            gpu_info = analyzer.get_gpu_info()
            print(f"🔧 Configuration GPU: {gpu_info}")
            
            try:
                # Analyse des compétences
                skills_analysis = analyzer.extract_skills(extracted_text)
                
                # Analyse de l'expérience
                experience_analysis = analyzer.extract_experience(extracted_text)
                
                # Calcul du score global
                overall_score = analyzer.calculate_overall_score({
                    'skills': skills_analysis,
                    'experience': experience_analysis,
                    'text_length': len(extracted_text)
                })
                
                print(f"✅ Analyse terminée - Score: {overall_score}% (GPU: {gpu_info.get('gpu_available', False)})")
                
            finally:
                # Nettoyage de la mémoire GPU après traitement
                analyzer.cleanup_gpu_memory()
            
            # Création de la candidature en base de données
            candidature = Candidature.objects.create(
                candidat=request.user,
                poste='Candidature spontanée',  # TODO: mettre des postes custom si on a le temps
                entreprise='CIVIA Corp.', # TODO: mettre entreprise custom si on a le temps
                cv=cv_file,
                status='en_attente',
                score_ia=overall_score,
                competences_extraites=skills_analysis,  # Correction: utiliser directement skills_analysis
                commentaires=f'CV analysé automatiquement. Score: {overall_score}% - GPU: {gpu_info.get("gpu_available", False)}'
            )
            
            # Nettoyage du fichier temporaire
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
            
            return JsonResponse({
                'success': True,
                'message': 'CV analysé avec succès !',
                'data': {
                    'candidature_id': candidature.id,
                    'score_ia': overall_score,
                    'competences_trouvees': len(skills_analysis.get('skills', [])),
                    'redirect_url': f'/account/{candidature.id}/'
                }
            })
            
        except Exception as e:
            # Nettoyage en cas d'erreur
            if 'full_file_path' in locals() and os.path.exists(full_file_path):
                os.remove(full_file_path)
            
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors du traitement: {str(e)}'
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


# page compte utilisateur
@login_required
def account_view(request):
    # Rediriger selon le rôle
    if request.user.role == 'recruteur' or request.user.role == 'admin':
        return redirect('recruiter-dashboard')
    else:
        return candidat_dashboard_view(request)


# Dashboard candidat
@login_required
def candidat_dashboard_view(request):
    # Récupérer les vraies candidatures de l'utilisateur connecté
    candidatures = Candidature.objects.filter(candidat=request.user).order_by('-created_at')
    
    # Calculer les statistiques réelles
    total_candidatures = candidatures.count()
    candidatures_en_attente = candidatures.filter(status='en_attente').count()
    candidatures_acceptees = candidatures.filter(status='acceptee').count()
    candidatures_refusees = candidatures.filter(status='refusee').count()
    
    # Calculer le score moyen (uniquement pour les candidatures avec score IA)
    candidatures_avec_score = candidatures.filter(score_ia__isnull=False)
    if candidatures_avec_score.exists():
        score_moyen = candidatures_avec_score.aggregate(
            moyenne=models.Avg('score_ia')
        )['moyenne']
        score_moyen = round(score_moyen, 1) if score_moyen else 0
    else:
        score_moyen = 0
    
    context = {
        'title': 'Mon Compte - Suivi des candidatures',
        'candidatures': candidatures,
        'user': request.user,
        'stats': {
            'total': total_candidatures,
            'en_attente': candidatures_en_attente,
            'acceptees': candidatures_acceptees,
            'refusees': candidatures_refusees,
            'score_moyen': score_moyen
        }
    }
    return render(request, 'pages/account.html', context)


# Dashboard recruteur
@login_required
def recruiter_dashboard_view(request):
    if request.user.role not in ['recruteur', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    # Récupérer toutes les candidatures (les recruteurs voient tout)
    candidatures = Candidature.objects.all().order_by('-created_at').select_related('candidat')
    
    # Calculer les statistiques réelles
    total_candidatures = candidatures.count()
    candidatures_nouvelles = candidatures.filter(status='en_attente').count()  # Nouveau = en_attente pour simplifier
    candidatures_en_cours = candidatures.filter(status='en_cours').count()
    candidatures_acceptees = candidatures.filter(status='acceptee').count()
    candidatures_refusees = candidatures.filter(status='refusee').count()
    
    # Statistiques IA
    candidatures_avec_score = candidatures.filter(score_ia__isnull=False)
    score_moyen_global = 0
    if candidatures_avec_score.exists():
        score_moyen_global = candidatures_avec_score.aggregate(
            moyenne=models.Avg('score_ia')
        )['moyenne']
        score_moyen_global = round(score_moyen_global, 1) if score_moyen_global else 0
    
    context = {
        'title': 'Dashboard Recruteur - Gestion des candidatures',
        'candidatures': candidatures[:20],  # Limiter à 20 pour la performance
        'user': request.user,
        'stats': {
            'total': total_candidatures,
            'nouveau': candidatures_nouvelles,
            'en_attente': candidatures_nouvelles,  # Alias
            'en_cours': candidatures_en_cours,
            'acceptees': candidatures_acceptees,
            'refusees': candidatures_refusees,
            'score_moyen': score_moyen_global
        }
    }
    return render(request, 'pages/recruiter_dashboard.html', context)


# Dashboard admin (placeholder)
@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    # Pour l'instant, rediriger vers le dashboard recruteur
    return recruiter_dashboard_view(request)


# page détails d'une candidature
@login_required
def candidature_detail_view(request, candidature_id):
    try:
        # Récupérer la candidature réelle depuis la base de données
        candidature = Candidature.objects.select_related('candidat').get(id=candidature_id)
        
        # Vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de voir cette candidature.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        # Timeline générique (à améliorer plus tard avec un modèle dédié)
        timeline_entries = [
            {'date': candidature.created_at.strftime('%Y-%m-%d'), 'action': 'Candidature soumise', 'status': 'completed'},
        ]
        
        if candidature.score_ia:
            timeline_entries.append({
                'date': candidature.created_at.strftime('%Y-%m-%d'), 
                'action': f'CV analysé par IA (Score: {candidature.score_ia}%)', 
                'status': 'completed'
            })
        
        if candidature.status == 'en_cours':
            timeline_entries.append({'date': '', 'action': 'En cours d\'examen par RH', 'status': 'current'})
        elif candidature.status == 'acceptee':
            timeline_entries.append({'date': '', 'action': 'Candidature acceptée !', 'status': 'completed'})
        elif candidature.status == 'refusee':
            timeline_entries.append({'date': '', 'action': 'Candidature non retenue', 'status': 'completed'})
        else:  # en_attente
            timeline_entries.append({'date': '', 'action': 'En attente d\'examen', 'status': 'current'})
        
        # Ajouter les étapes futures si pas encore terminé
        if candidature.status not in ['acceptee', 'refusee']:
            timeline_entries.extend([
                {'date': '', 'action': 'Entretien téléphonique', 'status': 'pending'},
                {'date': '', 'action': 'Entretien technique', 'status': 'pending'},
                {'date': '', 'action': 'Décision finale', 'status': 'pending'}
            ])
        
        # Ajouter la timeline à l'objet candidature pour le template
        candidature.timeline = timeline_entries
        
        context = {
            'title': f'Candidature - {candidature.poste}',
            'candidature': candidature,
            'user': request.user
        }
        return render(request, 'pages/candidature_detail.html', context)
        
    except Candidature.DoesNotExist:
        messages.error(request, 'Candidature non trouvée.')
        return redirect('account')
