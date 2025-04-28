from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils import timezone
from django.shortcuts import redirect
from .models import User, Structure, Formation, UserFormation, Notification

# Custom admin for the User model
class UserAdmin(BaseUserAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'is_active', 'user_cree_date')
    list_filter = ('user_role', 'is_active', 'structure')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'structure__structure_varchar')
    ordering = ('user_email',)
    readonly_fields = ('user_cree_date', 'user_miseajour_date')

    fieldsets = (
        (None, {'fields': ('user_email', 'user_username', 'password')}),
        ('Personal Info', {'fields': ('user_firstname', 'user_lastname', 'user_role', 'structure')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Audit Info', {'fields': ('user_cree_par', 'user_miseajour_par', 'user_miseajour_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_email', 'user_username', 'password1', 'password2', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'is_active', 'is_staff'),
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
    list_display = ('formation_titre', 'formation_ref', 'formation_niveau', 'formation_cout', 'formation_pays', 'structure')
    list_filter = ('formation_niveau', 'formation_pays', 'structure')
    search_fields = ('formation_titre', 'formation_ref', 'structure__structure_varchar')
    ordering = ('formation_titre',)
    exclude = ('user_id',)

# Admin for UserFormation model
class UserFormationAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'get_valide_date', 'action_buttons')
    list_filter = ('state_formation', 'date_inscription')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)

    def get_valide_date(self, obj):
        """Display validation date or '-' if not validated."""
        return obj.valide_date if obj.valide_date else '-'
    get_valide_date.short_description = 'Validation Date'

    def action_buttons(self, obj):
        """Render buttons for validating or canceling a pending formation."""
        if obj.state_formation == 'pending':
            validate_url = reverse('admin:validate_user_formation', args=[obj.pk])
            cancel_url = reverse('admin:cancel_user_formation', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="margin-right: 5px; padding: 5px 10px; background-color: #28a745; color: white; text-decoration: none; border-radius: 3px;">Validate</a>'
                '<a class="button" href="{}" style="padding: 5px 10px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 3px;">Cancel</a>',
                validate_url, cancel_url
            )
        return '-'
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    def get_urls(self):
        """Add custom URLs for validate and cancel actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/validate/',
                self.admin_site.admin_view(self.validate_user_formation),
                name='validate_user_formation'
            ),
            path(
                '<int:pk>/cancel/',
                self.admin_site.admin_view(self.cancel_user_formation),
                name='cancel_user_formation'
            ),
        ]
        return custom_urls + urls

    def validate_user_formation(self, request, pk):
        """Handle validation of a user formation."""
        user_formation = self.get_object(request, pk)
        if user_formation and user_formation.state_formation == 'pending':
            user_formation.valider_par(request.user.user_username)
            self.message_user(request, f"Participation of {user_formation.user.user_username} in {user_formation.formation.formation_titre} validated.")
        return redirect('admin:users_userformation_changelist')

    def cancel_user_formation(self, request, pk):
        """Handle cancellation of a user formation."""
        user_formation = self.get_object(request, pk)
        if user_formation and user_formation.state_formation == 'pending':
            user_formation.annuler_inscription()
            self.message_user(request, f"Participation of {user_formation.user.user_username} in {user_formation.formation.formation_titre} canceled.")
        return redirect('admin:users_userformation_changelist')

# Admin for Notification model
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__user_username', 'message')
    ordering = ('-created_at',)

# Register models with their respective admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(UserFormation, UserFormationAdmin)
admin.site.register(Notification, NotificationAdmin)