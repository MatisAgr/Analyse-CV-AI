# TEMPLATE VIEWS - Vues pour les templates HTML
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
import os
import json
import mimetypes

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
    Vue pour gérer l'upload de CV et lettre de motivation avec analyse IA
    """
    if request.method == 'POST':
        try:
            # vérification qu'un fichier CV est présent
            if 'cv' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'Aucun fichier CV trouvé.'
                })
            
            cv_file = request.FILES['cv']
            lettre_file = request.FILES.get('lettre_motivation')  # optionnel
            
            # validation du type de fichier CV
            allowed_extensions = ['pdf', 'doc', 'docx']
            cv_extension = cv_file.name.split('.')[-1].lower()
            
            if cv_extension not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'message': 'Format de fichier CV non supporté. Utilisez PDF, DOC ou DOCX.'
                })
            
            # validation du type de lettre de motivation si présente
            if lettre_file:
                lettre_extension = lettre_file.name.split('.')[-1].lower()
                if lettre_extension not in allowed_extensions:
                    return JsonResponse({
                        'success': False,
                        'message': 'Format de fichier lettre de motivation non supporté. Utilisez PDF, DOC ou DOCX.'
                    })
            
            # sauvegarde temporaire du fichier CV
            cv_path = default_storage.save(f'temp_cv/{cv_file.name}', ContentFile(cv_file.read()))
            cv_full_path = os.path.join(default_storage.location, cv_path)
            
            lettre_full_path = None
            if lettre_file:
                lettre_path = default_storage.save(f'temp_lettre/{lettre_file.name}', ContentFile(lettre_file.read()))
                lettre_full_path = os.path.join(default_storage.location, lettre_path)
            
            extractor = TextExtractor()
            
            if cv_extension == 'pdf':
                extraction_result = extractor.extract_from_pdf(cv_full_path)
            else:  # doc/docx
                extraction_result = extractor.extract_from_docx(cv_full_path)
            
            if not extraction_result['success']:
                # nettoyage des fichiers temporaires
                if os.path.exists(cv_full_path):
                    os.remove(cv_full_path)
                if lettre_full_path and os.path.exists(lettre_full_path):
                    os.remove(lettre_full_path)
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de l\'extraction du texte du CV: {extraction_result["error"]}'
                })
            
            extracted_text = extraction_result['text']
            
            # analyse IA du CV avec optimisations GPU
            analyzer = CVAnalyzer()
            
            # affichage des informations GPU
            gpu_info = analyzer.get_gpu_info()
            print(f"🔧 Configuration GPU: {gpu_info}")
            
            try:
                # analyse des compétences
                skills_analysis = analyzer.extract_skills(extracted_text)

                # analyse de l'expérience
                experience_analysis = analyzer.extract_experience(extracted_text)
                
                # calcul du score global
                overall_score = analyzer.calculate_overall_score({
                    'skills': skills_analysis,
                    'experience': experience_analysis,
                    'text_length': len(extracted_text)
                })
                
                print(f"✅ Analyse terminée - Score: {overall_score}% (GPU: {gpu_info.get('gpu_available', False)})")
                
            finally:
                analyzer.cleanup_gpu_memory()
            
            candidature = Candidature.objects.create(
                candidat=request.user,
                poste='Candidature spontanée',  # TODO: mettre des postes custom si on a le temps
                entreprise='CIVIA Corp.', # TODO: mettre entreprise custom si on a le temps
                cv=cv_file,
                lettre_motivation=lettre_file if lettre_file else None,
                status='en_attente',
                score_ia=overall_score,
                competences_extraites=skills_analysis,
                commentaires=f'CV analysé automatiquement. Score: {overall_score}% - GPU: {gpu_info.get("gpu_available", False)}'
            )
            
            # nettoyage des fichiers temporaires
            if os.path.exists(cv_full_path):
                os.remove(cv_full_path)
            if lettre_full_path and os.path.exists(lettre_full_path):
                os.remove(lettre_full_path)
            
            return JsonResponse({
                'success': True,
                'message': 'Candidature analysée avec succès !',
                'data': {
                    'candidature_id': candidature.id,
                    'score_ia': overall_score,
                    'competences_trouvees': len(skills_analysis.get('skills', [])),
                    'documents_soumis': {
                        'cv': cv_file.name,
                        'lettre': lettre_file.name if lettre_file else None
                    },
                    'redirect_url': f'/account/{candidature.id}/'
                }
            })
            
        except Exception as e:
            # Nettoyage en cas d'erreur
            if 'cv_full_path' in locals() and os.path.exists(cv_full_path):
                os.remove(cv_full_path)
            if 'lettre_full_path' in locals() and lettre_full_path and os.path.exists(lettre_full_path):
                os.remove(lettre_full_path)
            
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors du traitement: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

# check si le user est co
def check_auth_status(request):
    if request.user.is_authenticated:
        # nom d'affichage
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
    if request.user.role == 'recruteur' or request.user.role == 'admin':
        return redirect('recruiter-dashboard')
    else:
        return candidat_dashboard_view(request)


# dashboard candidat
@login_required
def candidat_dashboard_view(request):
    candidatures = Candidature.objects.filter(candidat=request.user).order_by('-created_at')
    
    # calculer les statistiques réelles
    total_candidatures = candidatures.count()
    candidatures_en_attente = candidatures.filter(status='en_attente').count()
    candidatures_acceptees = candidatures.filter(status='acceptee').count()
    candidatures_refusees = candidatures.filter(status='refusee').count()
    
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


# dashboard recruteur
@login_required
def recruiter_dashboard_view(request):
    if request.user.role not in ['recruteur', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    candidatures = Candidature.objects.all().order_by('-created_at').select_related('candidat')
    
    total_candidatures = candidatures.count()
    candidatures_nouvelles = candidatures.filter(status='en_attente').count()  # nouveau = en_attente pour simplifier
    candidatures_en_cours = candidatures.filter(status='en_cours').count()
    candidatures_acceptees = candidatures.filter(status='acceptee').count()
    candidatures_refusees = candidatures.filter(status='refusee').count()
    
    # statistiques IA
    candidatures_avec_score = candidatures.filter(score_ia__isnull=False)
    score_moyen_global = 0
    if candidatures_avec_score.exists():
        score_moyen_global = candidatures_avec_score.aggregate(
            moyenne=models.Avg('score_ia')
        )['moyenne']
        score_moyen_global = round(score_moyen_global, 1) if score_moyen_global else 0
    
    context = {
        'title': 'Dashboard Recruteur - Gestion des candidatures',
        'candidatures': candidatures[:20],  # limiter à 20 pour la performance
        'user': request.user,
        'stats': {
            'total': total_candidatures,
            'nouveau': candidatures_nouvelles,
            'en_attente': candidatures_nouvelles, 
            'en_cours': candidatures_en_cours,
            'acceptees': candidatures_acceptees,
            'refusees': candidatures_refusees,
            'score_moyen': score_moyen_global
        }
    }
    return render(request, 'pages/recruiter_dashboard.html', context)


# dashboard admin (placeholder)
@login_required
def admin_dashboard_view(request):
    if request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    #pour l'instant, rediriger vers le dashboard recruteur
    return recruiter_dashboard_view(request)


# page détails d'une candidature
@login_required
def candidature_detail_view(request, candidature_id):
    try:
        # récupérer la candidature réelle depuis la base de données
        candidature = Candidature.objects.select_related('candidat').get(id=candidature_id)
        
        # vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de voir cette candidature.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        # timeline générique
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
        
        if candidature.status not in ['acceptee', 'refusee']:
            timeline_entries.extend([
                {'date': '', 'action': 'Entretien téléphonique', 'status': 'pending'},
                {'date': '', 'action': 'Entretien technique', 'status': 'pending'},
                {'date': '', 'action': 'Décision finale', 'status': 'pending'}
            ])
      
        candidature.timeline = timeline_entries

        # statistiques du candidat
        candidat = candidature.candidat
        candidat_qs = Candidature.objects.filter(candidat=candidat)
        total_candidat = candidat_qs.count()
        accepte_candidat = candidat_qs.filter(status='acceptee').count()
        # scores uniquement lorsque non null
        qs_scores = candidat_qs.filter(score_ia__isnull=False)
        avg_score_candidat = None
        if qs_scores.exists():
            avg = qs_scores.aggregate(avg=models.Avg('score_ia'))['avg']
            if avg is not None:
                avg_score_candidat = round(avg, 1)

        candidate_stats = {
            'total': total_candidat,
            'accepted': accepte_candidat,
            'avg_score': avg_score_candidat
        }

        context = {
            'title': f'Candidature - {candidature.poste}',
            'candidature': candidature,
            'user': request.user,
                'candidate_stats': candidate_stats
        }
        return render(request, 'pages/candidature_detail.html', context)
        
    except Candidature.DoesNotExist:
        messages.error(request, 'Candidature non trouvée.')
        return redirect('account')


# actions pour accepter/refuser une candidature
@login_required
def accepter_candidature(request, candidature_id):
    """
    Vue pour accepter une candidature (réservée aux recruteurs/admins)
    """
    if request.user.role not in ['recruteur', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        if candidature.status in ['acceptee', 'refusee']:
            messages.warning(request, f'Cette candidature a déjà été {candidature.get_status_display().lower()}.')
        else:
            candidature.status = 'acceptee'
            
            commentaire_auto = f"Candidature acceptée par {request.user.first_name} {request.user.last_name} ({request.user.email}) le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            if candidature.commentaires:
                candidature.commentaires += f"\n\n--- ACCEPTATION ---\n{commentaire_auto}"
            else:
                candidature.commentaires = commentaire_auto
            
            candidature.save()
            
            messages.success(request, f'Candidature de {candidature.candidat.first_name} {candidature.candidat.last_name} acceptée avec succès!')
        
        # retourner vers le dashboard recruteur ou la page de détails selon la source
        if request.GET.get('from') == 'detail':
            return redirect('candidature-detail', candidature_id=candidature_id)
        else:
            return redirect('recruiter-dashboard')
            
    except Candidature.DoesNotExist:
        messages.error(request, 'Candidature non trouvée.')
        return redirect('recruiter-dashboard')

# fini pour le candidat
@login_required
def refuser_candidature(request, candidature_id):
 
    if request.user.role not in ['recruteur', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        if candidature.status in ['acceptee', 'refusee']:
            messages.warning(request, f'Cette candidature a déjà été {candidature.get_status_display().lower()}.')
        else:
            candidature.status = 'refusee'
            
            commentaire_auto = f"Candidature refusée par {request.user.first_name} {request.user.last_name} ({request.user.email}) le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            if candidature.commentaires:
                candidature.commentaires += f"\n\n--- REFUS ---\n{commentaire_auto}"
            else:
                candidature.commentaires = commentaire_auto
                
            candidature.save()
            
            messages.success(request, f'Candidature de {candidature.candidat.first_name} {candidature.candidat.last_name} refusée.')
        
        # retourner vers le dashboard recruteur 
        if request.GET.get('from') == 'detail':
            return redirect('candidature-detail', candidature_id=candidature_id)
        else:
            return redirect('recruiter-dashboard')
            
    except Candidature.DoesNotExist:
        messages.error(request, 'Candidature non trouvée.')
        return redirect('recruiter-dashboard')


@login_required
def changer_statut_candidature(request, candidature_id):
    """
    Vue pour changer le statut d'une candidature (en_cours, en_attente, etc.)
    """
    if request.user.role not in ['recruteur', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('account')
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        
        if nouveau_statut not in ['en_attente', 'en_cours', 'acceptee', 'refusee']:
            messages.error(request, 'Statut invalide.')
            return redirect('recruiter-dashboard')
        
        try:
            candidature = Candidature.objects.get(id=candidature_id)
            ancien_statut = candidature.get_status_display()
            candidature.status = nouveau_statut
            
            # Ajouter un commentaire de changement de statut
            commentaire_auto = f"Statut changé de '{ancien_statut}' vers '{candidature.get_status_display()}' par {request.user.first_name} {request.user.last_name} le {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            if candidature.commentaires:
                candidature.commentaires += f"\n\n--- CHANGEMENT DE STATUT ---\n{commentaire_auto}"
            else:
                candidature.commentaires = commentaire_auto
                
            candidature.save()
            
            messages.success(request, f'Statut de la candidature mis à jour vers "{candidature.get_status_display()}"')
            
        except Candidature.DoesNotExist:
            messages.error(request, 'Candidature non trouvée.')
    
    return redirect('recruiter-dashboard')


@login_required
def download_cv(request, candidature_id):
    """
    Vue pour télécharger le CV d'une candidature
    """
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        # Vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de télécharger ce document.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        if not candidature.cv:
            raise Http404("CV non trouvé")
        
        # Obtenir le fichier
        file_path = candidature.cv.path
        if not os.path.exists(file_path):
            raise Http404("Fichier CV non trouvé sur le disque")
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # Lire le fichier et retourner la réponse
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{candidature.cv.name.split("/")[-1]}"'
            return response
            
    except Candidature.DoesNotExist:
        raise Http404("Candidature non trouvée")


@login_required
def download_lettre(request, candidature_id):
    """
    Vue pour télécharger la lettre de motivation d'une candidature
    """
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        # Vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de télécharger ce document.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        if not candidature.lettre_motivation:
            raise Http404("Lettre de motivation non trouvée")
        
        # Obtenir le fichier
        file_path = candidature.lettre_motivation.path
        if not os.path.exists(file_path):
            raise Http404("Fichier lettre de motivation non trouvé sur le disque")
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # Lire le fichier et retourner la réponse
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{candidature.lettre_motivation.name.split("/")[-1]}"'
            return response
            
    except Candidature.DoesNotExist:
        raise Http404("Candidature non trouvée")


@login_required
def view_cv(request, candidature_id):
    """
    Vue pour visualiser le CV dans le navigateur
    """
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        # Vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de voir ce document.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        if not candidature.cv:
            raise Http404("CV non trouvé")
        
        # Obtenir le fichier
        file_path = candidature.cv.path
        if not os.path.exists(file_path):
            raise Http404("Fichier CV non trouvé sur le disque")
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # Lire le fichier et retourner pour visualisation
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mime_type)
            # Pas de Content-Disposition pour permettre la visualisation dans le navigateur
            return response
            
    except Candidature.DoesNotExist:
        raise Http404("Candidature non trouvée")


@login_required
def view_lettre(request, candidature_id):
    """
    Vue pour visualiser la lettre de motivation dans le navigateur
    """
    try:
        candidature = Candidature.objects.get(id=candidature_id)
        
        # Vérifier les permissions
        if request.user.role == 'candidat' and candidature.candidat != request.user:
            messages.error(request, 'Vous n\'avez pas l\'autorisation de voir ce document.')
            return redirect('account')
        elif request.user.role not in ['candidat', 'recruteur', 'admin']:
            messages.error(request, 'Accès non autorisé.')
            return redirect('home')
        
        if not candidature.lettre_motivation:
            raise Http404("Lettre de motivation non trouvée")
        
        # Obtenir le fichier
        file_path = candidature.lettre_motivation.path
        if not os.path.exists(file_path):
            raise Http404("Fichier lettre de motivation non trouvé sur le disque")
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # Lire le fichier et retourner pour visualisation
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mime_type)
            # Pas de Content-Disposition pour permettre la visualisation dans le navigateur
            return response
            
    except Candidature.DoesNotExist:
        raise Http404("Candidature non trouvée")
