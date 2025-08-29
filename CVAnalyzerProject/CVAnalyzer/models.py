from django.db import models
from django.contrib.auth.models import AbstractUser, Group
import os
from django.core.validators import FileExtensionValidator


def upload_cv_to(instance, filename):
    """Fonction pour définir où stocker les CV"""
    # Organiser par utilisateur: cv/user_123/cv_nom.pdf
    return f'cv/user_{instance.candidat.id}/{filename}'


def upload_lettre_to(instance, filename):
    """Fonction pour définir où stocker les lettres de motivation"""
    return f'lettres/user_{instance.candidat.id}/{filename}'

class User(AbstractUser):
    """
    Modèle utilisateur étendu avec système de rôles
    pour la gestion des ressources humaines
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    
    # Email comme identifiant unique
    email = models.EmailField(unique=True, help_text="Adresse email (identifiant de connexion)")
    
    # Username généré automatiquement à partir de l'email
    username = models.CharField(max_length=150, unique=True, help_text="Nom d'utilisateur généré automatiquement")
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='candidat',
        help_text="Rôle de l'utilisateur dans le système"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Numéro de téléphone"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Utiliser email comme identifiant de connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username
    
    def save(self, *args, **kwargs):
        """
        Override de save pour assigner automatiquement 
        les groupes selon le rôle
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.assign_role_group()
    
    def assign_role_group(self):
        """
        Assigne l'utilisateur au groupe correspondant à son rôle
        """
        # Mapping rôle -> nom du groupe
        role_group_mapping = {
            'admin': 'Administrateurs',
            'recruteur': 'Recruteurs', 
            'candidat': 'Candidats'
        }
        
        group_name = role_group_mapping.get(self.role)
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.clear()  # Nettoyer les anciens groupes
            self.groups.add(group)
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


class Candidature(models.Model):
    """
    Modèle pour gérer les candidatures des utilisateurs
    """
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours d\'examen'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    # Relations
    candidat = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='candidatures',
        help_text="Candidat qui postule"
    )
    
    # Informations sur le poste
    poste = models.CharField(
        max_length=200,
        help_text="Intitulé du poste"
    )
    entreprise = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nom de l'entreprise"
    )
    
    # Fichiers
    cv = models.FileField(
        upload_to=upload_cv_to,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="CV au format PDF, DOC ou DOCX"
    )
    lettre_motivation = models.FileField(
        upload_to=upload_lettre_to,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        null=True,
        help_text="Lettre de motivation (optionnelle)"
    )
    
    # Statut et suivi
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
        help_text="Statut de la candidature"
    )
    
    # Analyse IA (pour plus tard)
    score_ia = models.FloatField(
        null=True,
        blank=True,
        help_text="Score d'analyse IA (0-100)"
    )
    competences_extraites = models.JSONField(
        default=list,
        blank=True,
        help_text="Compétences extraites par IA"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Commentaires recruteur
    commentaires = models.TextField(
        blank=True,
        help_text="Commentaires du recruteur"
    )
    
    def __str__(self):
        return f"{self.candidat.email} - {self.poste} ({self.get_status_display()})"
    
    def delete(self, *args, **kwargs):
        """Supprimer les fichiers lors de la suppression de la candidature"""
        if self.cv:
            if os.path.isfile(self.cv.path):
                os.remove(self.cv.path)
        if self.lettre_motivation:
            if os.path.isfile(self.lettre_motivation.path):
                os.remove(self.lettre_motivation.path)
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ['-created_at']


class AIModel(models.Model):
    """
    Modèle pour gérer les modèles d'IA utilisés pour l'analyse
    """
    MODEL_TYPE_CHOICES = [
        ('transformer', 'Transformer'),
        ('bert', 'BERT'),
        ('gpt', 'GPT'),
        ('sentence_transformer', 'Sentence Transformer'),
    ]
    
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    model_path = models.CharField(max_length=500)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class Candidate(models.Model):
    """
    Modèle pour les candidats (peut être utilisé indépendamment du User)
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class JobPosition(models.Model):
    """
    Modèle pour les postes à pourvoir
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    required_experience_years = models.IntegerField(default=0)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title


class Resume(models.Model):
    """
    Modèle pour les CV uploadés
    """
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True)
    extracted_skills = models.JSONField(default=list)
    extracted_experience = models.JSONField(default=list)
    extracted_education = models.JSONField(default=list)
    extracted_languages = models.JSONField(default=list)
    file_size = models.IntegerField(default=0)
    file_type = models.CharField(max_length=10)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate} - {self.original_filename}"


class CVAnalysis(models.Model):
    """
    Modèle pour les analyses de CV par IA
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='cv_analyses')
    overall_score = models.FloatField(default=0.0)
    skills_match_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    analysis_details = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-overall_score']
        unique_together = [('resume', 'job_position')]
    
    def __str__(self):
        return f"{self.resume.candidate} - {self.job_position} ({self.overall_score}%)"
