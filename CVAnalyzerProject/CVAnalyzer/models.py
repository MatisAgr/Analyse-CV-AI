from django.db import models
from django.contrib.auth.models import AbstractUser, Group
import os
from django.core.validators import FileExtensionValidator


def upload_cv_to(instance, filename):
    # Organiser par utilisateur: cv/user_123/cv_nom.pdf
    return f'cv/user_{instance.candidat.id}/{filename}'


def upload_lettre_to(instance, filename):
    return f'lettres/user_{instance.candidat.id}/{filename}'

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    
    # email comme identifiant unique
    email = models.EmailField(unique=True, help_text="Adresse email (identifiant de connexion)")
    
    # username généré automatiquement à partir de l'email
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
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.assign_role_group()
    
    def assign_role_group(self):
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
    
    # suppression des fichiers associés
    def delete(self, *args, **kwargs):
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