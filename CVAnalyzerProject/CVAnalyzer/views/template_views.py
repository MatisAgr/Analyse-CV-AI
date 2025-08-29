# TEMPLATE VIEWS - Vues pour les templates HTML
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
    # Données fictives pour les candidatures
    candidatures_fictives = [
        {
            'id': 1,
            'poste': 'Développeur Full Stack',
            'entreprise': 'TechCorp',
            'date_candidature': '2025-08-25',
            'statut': 'en_attente',
            'statut_display': 'En attente',
            'statut_color': 'yellow',
            'score_ia': 85,
            'cv_nom': 'CV_John_Doe.pdf',
            'lettre_nom': 'Lettre_motivation.pdf',
            'commentaires': 'Profil intéressant, compétences techniques solides.'
        },
        {
            'id': 2,
            'poste': 'Chef de Projet Digital',
            'entreprise': 'InnovCorp',
            'date_candidature': '2025-08-20',
            'statut': 'accepte',
            'statut_display': 'Accepté',
            'statut_color': 'green',
            'score_ia': 92,
            'cv_nom': 'CV_John_Doe_v2.pdf',
            'lettre_nom': 'Lettre_chef_projet.pdf',
            'commentaires': 'Excellent profil ! Expérience parfaitement adaptée au poste.'
        },
        {
            'id': 3,
            'poste': 'Développeur Frontend',
            'entreprise': 'StartupXYZ',
            'date_candidature': '2025-08-15',
            'statut': 'rejete',
            'statut_display': 'Rejeté',
            'statut_color': 'red',
            'score_ia': 68,
            'cv_nom': 'CV_John_Doe_old.pdf',
            'lettre_nom': None,
            'commentaires': 'Manque d\'expérience en React. Candidature ne correspond pas aux exigences.'
        }
    ]
    
    # Calculer les statistiques
    total_candidatures = len(candidatures_fictives)
    candidatures_en_attente = len([c for c in candidatures_fictives if c['statut'] == 'en_attente'])
    candidatures_acceptees = len([c for c in candidatures_fictives if c['statut'] == 'accepte'])
    score_moyen = sum(c['score_ia'] for c in candidatures_fictives) // len(candidatures_fictives) if candidatures_fictives else 0
    
    context = {
        'title': 'Mon Compte - Suivi des candidatures',
        'candidatures': candidatures_fictives,
        'user': request.user,
        'stats': {
            'total': total_candidatures,
            'en_attente': candidatures_en_attente,
            'acceptees': candidatures_acceptees,
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
    
    # Données fictives pour toutes les candidatures (vue recruteur)
    toutes_candidatures = [
        {
            'id': 1,
            'candidat_nom': 'John Doe',
            'candidat_initiales': 'JD',
            'candidat_email': 'john.doe@email.com',
            'poste': 'Développeur Full Stack',
            'entreprise': 'TechCorp',
            'date_candidature': '2025-08-25',
            'statut': 'en_attente',
            'statut_display': 'En attente',
            'statut_color': 'yellow',
            'score_ia': 85,
            'cv_nom': 'CV_John_Doe.pdf',
            'lettre_nom': 'Lettre_motivation.pdf',
            'urgent': False
        },
        {
            'id': 2,
            'candidat_nom': 'Jane Smith',
            'candidat_initiales': 'JS',
            'candidat_email': 'jane.smith@email.com',
            'poste': 'Designer UX/UI',
            'entreprise': 'CreativeCorp',
            'date_candidature': '2025-08-24',
            'statut': 'en_revision',
            'statut_display': 'En révision',
            'statut_color': 'blue',
            'score_ia': 91,
            'cv_nom': 'CV_Jane_Smith.pdf',
            'lettre_nom': 'Lettre_Designer.pdf',
            'urgent': False
        },
        {
            'id': 3,
            'candidat_nom': 'Mike Johnson',
            'candidat_initiales': 'MJ',
            'candidat_email': 'mike.j@email.com',
            'poste': 'Chef de Projet Digital',
            'entreprise': 'InnovCorp',
            'date_candidature': '2025-08-20',
            'statut': 'accepte',
            'statut_display': 'Accepté',
            'statut_color': 'green',
            'score_ia': 92,
            'cv_nom': 'CV_Mike_Johnson.pdf',
            'lettre_nom': 'Lettre_chef_projet.pdf',
            'urgent': False
        },
        {
            'id': 4,
            'candidat_nom': 'Sarah Wilson',
            'candidat_initiales': 'SW',
            'candidat_email': 'sarah.w@email.com',
            'poste': 'Développeur Frontend',
            'entreprise': 'StartupXYZ',
            'date_candidature': '2025-08-15',
            'statut': 'rejete',
            'statut_display': 'Rejeté',
            'statut_color': 'red',
            'score_ia': 68,
            'cv_nom': 'CV_Sarah_Wilson.pdf',
            'lettre_nom': None,
            'urgent': False
        },
        {
            'id': 5,
            'candidat_nom': 'Alex Brown',
            'candidat_initiales': 'AB',
            'candidat_email': 'alex.brown@email.com',
            'poste': 'Data Scientist',
            'entreprise': 'DataCorp',
            'date_candidature': '2025-08-28',
            'statut': 'nouveau',
            'statut_display': 'Nouveau',
            'statut_color': 'purple',
            'score_ia': 88,
            'cv_nom': 'CV_Alex_Brown.pdf',
            'lettre_nom': 'Lettre_DataScience.pdf',
            'urgent': False
        }
    ]
    
    # Calculer les statistiques
    total_candidatures = len(toutes_candidatures)
    nouveau = len([c for c in toutes_candidatures if c['statut'] == 'nouveau'])
    en_attente = len([c for c in toutes_candidatures if c['statut'] == 'en_attente'])
    acceptees = len([c for c in toutes_candidatures if c['statut'] == 'accepte'])
    
    context = {
        'title': 'Dashboard Recruteur - Gestion des candidatures',
        'candidatures': toutes_candidatures,
        'user': request.user,
        'stats': {
            'total': total_candidatures,
            'nouveau': nouveau,
            'en_attente': en_attente,
            'acceptees': acceptees,
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
    # Données fictives pour les candidatures (même structure que account_view)
    candidatures_fictives = [
        {
            'id': 1,
            'poste': 'Développeur Full Stack',
            'entreprise': 'TechCorp',
            'date_candidature': '2025-08-25',
            'statut': 'en_attente',
            'statut_display': 'En attente',
            'statut_color': 'yellow',
            'score_ia': 85,
            'cv_nom': 'CV_John_Doe.pdf',
            'lettre_nom': 'Lettre_motivation.pdf',
            'commentaires': 'Profil intéressant, compétences techniques solides.',
            'competences_extraites': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker'],
            'points_forts': [
                'Expérience solide en développement web',
                'Maîtrise des frameworks modernes',
                'Bonne connaissance des bases de données'
            ],
            'points_amelioration': [
                'Manque d\'expérience en DevOps',
                'Pourrait approfondir les tests unitaires'
            ],
            'timeline': [
                {'date': '2025-08-25', 'action': 'Candidature soumise', 'status': 'completed'},
                {'date': '2025-08-26', 'action': 'CV analysé par IA', 'status': 'completed'},
                {'date': '2025-08-27', 'action': 'En cours de révision RH', 'status': 'current'},
                {'date': '', 'action': 'Entretien téléphonique', 'status': 'pending'},
                {'date': '', 'action': 'Entretien technique', 'status': 'pending'},
                {'date': '', 'action': 'Décision finale', 'status': 'pending'}
            ]
        },
        {
            'id': 2,
            'poste': 'Chef de Projet Digital',
            'entreprise': 'InnovCorp',
            'date_candidature': '2025-08-20',
            'statut': 'accepte',
            'statut_display': 'Accepté',
            'statut_color': 'green',
            'score_ia': 92,
            'cv_nom': 'CV_John_Doe_v2.pdf',
            'lettre_nom': 'Lettre_chef_projet.pdf',
            'commentaires': 'Excellent profil ! Expérience parfaitement adaptée au poste.',
            'competences_extraites': ['Gestion de projet', 'Scrum', 'Leadership', 'Digital', 'Analytics'],
            'points_forts': [
                'Leadership naturel et expérience managériale',
                'Excellente connaissance des méthodologies agiles',
                'Vision stratégique du digital'
            ],
            'points_amelioration': [],
            'timeline': [
                {'date': '2025-08-20', 'action': 'Candidature soumise', 'status': 'completed'},
                {'date': '2025-08-21', 'action': 'CV analysé par IA', 'status': 'completed'},
                {'date': '2025-08-22', 'action': 'Pré-sélectionné par RH', 'status': 'completed'},
                {'date': '2025-08-24', 'action': 'Entretien téléphonique réussi', 'status': 'completed'},
                {'date': '2025-08-26', 'action': 'Entretien final réussi', 'status': 'completed'},
                {'date': '2025-08-28', 'action': 'Candidature acceptée !', 'status': 'completed'}
            ]
        },
        {
            'id': 3,
            'poste': 'Développeur Frontend',
            'entreprise': 'StartupXYZ',
            'date_candidature': '2025-08-15',
            'statut': 'rejete',
            'statut_display': 'Rejeté',
            'statut_color': 'red',
            'score_ia': 68,
            'cv_nom': 'CV_John_Doe_old.pdf',
            'lettre_nom': None,
            'commentaires': 'Manque d\'expérience en React. Candidature ne correspond pas aux exigences.',
            'competences_extraites': ['HTML', 'CSS', 'JavaScript', 'Vue.js'],
            'points_forts': [
                'Bases solides en HTML/CSS',
                'Créativité dans le design'
            ],
            'points_amelioration': [
                'Manque d\'expérience avec React',
                'Portfolio insuffisant',
                'Pas de lettre de motivation'
            ],
            'timeline': [
                {'date': '2025-08-15', 'action': 'Candidature soumise', 'status': 'completed'},
                {'date': '2025-08-16', 'action': 'CV analysé par IA', 'status': 'completed'},
                {'date': '2025-08-17', 'action': 'Rejeté par RH', 'status': 'completed'}
            ]
        }
    ]
    
    # Trouver la candidature par ID
    candidature = next((c for c in candidatures_fictives if c['id'] == candidature_id), None)
    
    if not candidature:
        messages.error(request, 'Candidature non trouvée.')
        return redirect('account')
    
    context = {
        'title': f'Candidature - {candidature["poste"]}',
        'candidature': candidature,
        'user': request.user
    }
    return render(request, 'pages/candidature_detail.html', context)
