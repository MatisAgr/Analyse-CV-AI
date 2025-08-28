from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration personnalisée pour le modèle User étendu
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    # Ajouter les champs personnalisés aux fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'created_at', 'updated_at')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """
        Override pour s'assurer que les groupes sont assignés
        """
        super().save_model(request, obj, form, change)
        obj.assign_role_group()

# Configuration du site admin
admin.site.site_header = "CV Analyser - Administration"
admin.site.site_title = "CV Analyser Admin"
admin.site.index_title = "Bienvenue dans l'administration"
