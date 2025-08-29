from django.db import models
from django.contrib.auth.models import AbstractUser, Group

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
    REQUIRED_FIELDS = ['username']  # username sera généré automatiquement
    
    def save(self, *args, **kwargs):
        """
        Override de save pour générer username et assigner automatiquement 
        les groupes selon le rôle
        """
        # Générer username unique à partir de l'email si pas défini
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # S'assurer que le username est unique
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
            
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
