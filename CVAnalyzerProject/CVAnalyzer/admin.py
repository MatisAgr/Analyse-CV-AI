from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Candidature  # Seulement les modèles existants


#admin en fonction du BaseUser
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'phone', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # overridz poue l'adapter à nos rôles
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.assign_role_group()

# admin des candidatures
@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('candidat_info', 'poste', 'entreprise', 'status', 'score_ia_display', 'created_at', 'has_files')
    list_filter = ('status', 'entreprise', 'created_at')
    search_fields = ('candidat__email', 'candidat__first_name', 'candidat__last_name', 'poste', 'entreprise')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations candidat', {
            'fields': ('candidat',)
        }),
        ('Informations poste', {
            'fields': ('poste', 'entreprise')
        }),
        ('Documents', {
            'fields': ('cv', 'lettre_motivation')
        }),
        ('Suivi', {
            'fields': ('status', 'commentaires')
        }),
        ('Analyse IA', {
            'fields': ('score_ia', 'competences_extraites'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def candidat_info(self, obj):
        return f"{obj.candidat.first_name} {obj.candidat.last_name} ({obj.candidat.email})"
    candidat_info.short_description = 'Candidat'
    
    def score_ia_display(self, obj):
        if obj.score_ia is not None:
            try:
                score = float(obj.score_ia)
                return f"{score:.1f}%"
            except (ValueError, TypeError):
                return "Erreur de score"
        return "Non analysé"
    score_ia_display.short_description = 'Score IA'
    
    def has_files(self, obj):
        files = []
        if obj.cv:
            files.append('CV')
        if obj.lettre_motivation:
            files.append('Lettre')
        return ', '.join(files) if files else 'Aucun'
    has_files.short_description = 'Documents'

# configuration du site admin
admin.site.site_header = "CV Analyser - Administration"
admin.site.site_title = "CV Analyser Admin"
admin.site.index_title = "Bienvenue dans l'administration"
