from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Structure, Formation, Session, UserFormation

# Custom admin for the User model
class UserAdmin(BaseUserAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'is_active', 'user_cree_date')
    list_filter = ('user_role', 'is_active')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname')
    ordering = ('user_email',)

    fieldsets = (
        (None, {'fields': ('user_email', 'user_username', 'password')}),
        ('Personal Info', {'fields': ('user_firstname', 'user_lastname', 'user_role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Audit Info', {'fields': ('user_cree_par', 'user_cree_date', 'user_miseajour_par', 'user_miseajour_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_email', 'user_username', 'password1', 'password2', 'user_firstname', 'user_lastname', 'user_role', 'is_active', 'is_staff'),
        }),
    )

# Admin for Structure model
class StructureAdmin(admin.ModelAdmin):
    list_display = ('structure_varchar', 'structure_code', 'structure_niveau', 'structure_cree_date')
    list_filter = ('structure_niveau',)
    search_fields = ('structure_varchar', 'structure_code')
    ordering = ('structure_varchar',)

# Admin for Formation model
class FormationAdmin(admin.ModelAdmin):
    list_display = ('formation_titre', 'formation_ref', 'formation_niveau', 'formation_cout', 'formation_pays', 'user_id')
    list_filter = ('formation_niveau', 'formation_pays')
    search_fields = ('formation_titre', 'formation_ref')
    ordering = ('formation_titre',)

# Admin for Session model
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_debut_date', 'session_fin_date', 'formation', 'session_cree_date')
    list_filter = ('session_debut_date', 'formation')
    search_fields = ('formation__formation_titre',)
    ordering = ('session_debut_date',)

# Admin for UserFormation model
class UserFormationAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'valide_date')
    list_filter = ('state_formation', 'date_inscription')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)

# Register models with their respective admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(UserFormation, UserFormationAdmin)