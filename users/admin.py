# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils import timezone
from django.shortcuts import redirect
from .models import User, Structure, Department, Formation, UserFormation, Notification

class UserAdmin(BaseUserAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'state', 'is_active', 'user_cree_date', 'action_buttons')
    list_filter = ('user_role', 'state', 'is_active', 'structure', 'department')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'structure__structure_varchar', 'department__department_name')
    ordering = ('user_email',)
    readonly_fields = ('user_cree_date', 'user_miseajour_date')

    fieldsets = (
        (None, {'fields': ('user_email', 'user_username', 'password')}),
        ('Personal Info', {'fields': ('user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'state')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Audit Info', {'fields': ('user_cree_par', 'user_miseajour_par', 'user_miseajour_date')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_email', 'user_username', 'password1', 'password2', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'state', 'is_active', 'is_staff'),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/approve/', self.admin_site.admin_view(self.approve_user), name='approve_user'),
            path('<int:pk>/reject/', self.admin_site.admin_view(self.reject_user), name='reject_user'),
        ]
        return custom_urls + urls

    def action_buttons(self, obj):
        if obj.state == 'pending':
            approve_url = reverse('admin:approve_user', args=[obj.pk])
            reject_url = reverse('admin:reject_user', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="margin-right: 5px; padding: 5px 10px; background-color: #28a745; color: white; text-decoration: none; border-radius: 3px;">Approve</a>'
                '<a class="button" href="{}" style="padding: 5px 10px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 3px;">Reject</a>',
                approve_url, reject_url
            )
        return '-'
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    def approve_user(self, request, pk):
        user = self.get_object(request, pk)
        if user and user.state == 'pending':
            user.state = 'approved'
            user.is_active = True
            user.save()
            Notification.objects.create(
                user=user,
                message="Your account has been approved. You can now log in."
            )
            self.message_user(request, f"User {user.user_username} approved.")
        return redirect('admin:users_user_changelist')

    def reject_user(self, request, pk):
        user = self.get_object(request, pk)
        if user and user.state == 'pending':
            user.state = 'rejected'
            user.is_active = False
            user.save()
            Notification.objects.create(
                user=user,
                message="Your account registration was rejected."
            )
            self.message_user(request, f"User {user.user_username} rejected.")
        return redirect('admin:users_user_changelist')

class UserDemand(User):
    class Meta:
        proxy = True
        verbose_name = 'User Demand'
        verbose_name_plural = 'User Demands'

class UserDemandAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'user_cree_date', 'action_buttons')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'structure__structure_varchar', 'department__department_name')
    ordering = ('user_cree_date',)

    def get_queryset(self, request):
        return User.objects.filter(state='pending')

    def action_buttons(self, obj):
        if obj.state == 'pending':
            approve_url = reverse('admin:users_userdemand_approve', args=[obj.pk])
            reject_url = reverse('admin:users_userdemand_reject', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="margin-right: 5px; padding: 5px 10px; background-color: #28a745; color: white; text-decoration: none; border-radius: 3px;">Approve</a>'
                '<a class="button" href="{}" style="padding: 5px 10px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 3px;">Reject</a>',
                approve_url, reject_url
            )
        return '-'
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/approve/', self.admin_site.admin_view(self.approve_user), name='users_userdemand_approve'),
            path('<int:pk>/reject/', self.admin_site.admin_view(self.reject_user), name='users_userdemand_reject'),
        ]
        return custom_urls + urls

    def approve_user(self, request, pk):
        user = self.get_object(request, pk)
        if user and user.state == 'pending':
            user.state = 'approved'
            user.is_active = True
            user.save()
            Notification.objects.create(
                user=user,
                message="Your account has been approved. You can now log in."
            )
            self.message_user(request, f"User demand {user.user_username} approved.")
        return redirect('admin:users_userdemand_changelist')

    def reject_user(self, request, pk):
        user = self.get_object(request, pk)
        if user and user.state == 'pending':
            user.state = 'rejected'
            user.is_active = False
            user.save()
            Notification.objects.create(
                user=user,
                message="Your account registration was rejected."
            )
            self.message_user(request, f"User demand {user.user_username} rejected.")
        return redirect('admin:users_userdemand_changelist')

class StructureAdmin(admin.ModelAdmin):
    list_display = ('structure_varchar', 'structure_code', 'structure_niveau', 'structure_cree_date')
    list_filter = ('structure_niveau',)
    search_fields = ('structure_varchar', 'structure_code')
    ordering = ('structure_varchar',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'department_code', 'structure', 'department_cree_date')
    list_filter = ('structure',)
    search_fields = ('department_name', 'department_code', 'structure__structure_varchar')
    ordering = ('department_name',)

class FormationAdmin(admin.ModelAdmin):
    list_display = ('formation_titre', 'formation_ref', 'formation_niveau', 'formation_cout', 'formation_pays', 'structure')
    list_filter = ('formation_niveau', 'formation_pays', 'structure')
    search_fields = ('formation_titre', 'formation_ref', 'structure__structure_varchar')
    ordering = ('formation_titre',)
    exclude = ('user_id',)

class UserFormationAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'get_valide_date', 'action_buttons')
    list_filter = ('state_formation', 'date_inscription')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)

    def get_valide_date(self, obj):
        return obj.valide_date if obj.valide_date else '-'
    get_valide_date.short_description = 'Validation Date'

    def action_buttons(self, obj):
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
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/validate/', self.admin_site.admin_view(self.validate_user_formation), name='validate_user_formation'),
            path('<int:pk>/cancel/', self.admin_site.admin_view(self.cancel_user_formation), name='cancel_user_formation'),
        ]
        return custom_urls + urls

    def validate_user_formation(self, request, pk):
        user_formation = self.get_object(request, pk)
        if user_formation and user_formation.state_formation == 'pending':
            user_formation.valider_par(request.user.user_username)
            self.message_user(request, f"Participation of {user_formation.user.user_username} in {user_formation.formation.formation_titre} validated.")
        return redirect('admin:users_userformation_changelist')

    def cancel_user_formation(self, request, pk):
        user_formation = self.get_object(request, pk)
        if user_formation and user_formation.state_formation == 'pending':
            user_formation.annuler_inscription()
            self.message_user(request, f"Participation of {user_formation.user.user_username} in {user_formation.formation.formation_titre} canceled.")
        return redirect('admin:users_userformation_changelist')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__user_username', 'message')
    ordering = ('-created_at',)

admin.site.register(User, UserAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(UserFormation, UserFormationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserDemand, UserDemandAdmin)