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
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
