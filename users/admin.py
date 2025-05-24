


from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils import timezone
from django import forms
from .models import User, Structure, Department, Formation, UserFormation, Notification

# Customize Admin Site
admin.site.site_header = "TMS"
admin.site.site_title = "TMS"
admin.site.index_title = ""

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('')

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'state', 'user_cree_date')
    list_filter = ('user_role', 'state', 'structure', 'department')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'structure__structure_varchar', 'department__department_name')
    ordering = ('user_email',)
    readonly_fields = ('user_cree_par', 'user_cree_date', 'user_miseajour_par', 'user_miseajour_date')
    actions = ['validate_users', 'refuse_users']

    fieldsets = (
        (None, {'fields': ('user_email', 'user_username', 'user_firstname', 'user_lastname')}),
        ('Details', {'fields': ('user_role', 'structure', 'department', 'state')}),
        ('Audit Info', {'fields': ('user_cree_par', 'user_cree_date', 'user_miseajour_par', 'user_miseajour_date')}),
    )



    def validate_users(self, request, queryset):
        updated = queryset.filter(state='pending').update(state='approved', is_active=True)
        for user in queryset.filter(state='pending'):
            Notification.objects.create(
                user=user,
                message=f"Your account has been validated. Welcome to TMS!",
            )
        self.message_user(request, f"{updated} user(s) successfully validated.")
    validate_users.short_description = "Validate selected users"

    def refuse_users(self, request, queryset):
        updated = queryset.filter(state='pending').update(state='rejected', is_active=False)
        for user in queryset.filter(state='pending'):
            Notification.objects.create(
                user=user,
                message=f"Your account request has been refused.",
            )
        self.message_user(request, f"{updated} user(s) successfully refused.")
    refuse_users.short_description = "Refuse selected users"

class AccountsDemandedAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'user_cree_date', 'validate_button', 'refuse_button')
    list_filter = ('user_role', 'structure', 'department')
    search_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'structure__structure_varchar', 'department__department_name')
    ordering = ('user_cree_date',)
    readonly_fields = ('user_email', 'user_username', 'user_firstname', 'user_lastname', 'user_role', 'structure', 'department', 'user_cree_par', 'user_cree_date', 'user_miseajour_par', 'user_miseajour_date')

    def get_queryset(self, request):
        qs = User.objects.filter(state='pending')
        if request.user.is_superuser and request.user.user_role != 'DRH':
            # Admins (non-DRH superusers) can see all pending accounts
            return qs
        elif request.user.user_role == 'DRH' and request.user.structure:
            # DRH users can only see pending accounts from their structure
            return qs.filter(structure=request.user.structure)
        return qs.none()  # Return empty queryset if user has no structure or invalid role

    def validate_button(self, obj):
        return format_html(
            '<a class="button validate" style="display:inline-block;padding:5px 10px;margin:0 5px;color:#fff;background-color:#28a745;border-radius:3px;font-size:12px;text-decoration:none;" href="{}">Validate</a>',
            reverse('admin:validate-user', args=[obj.pk])
        )
    validate_button.short_description = 'Validate'
    validate_button.admin_order_field = 'user_cree_date'

    def refuse_button(self, obj):
        return format_html(
            '<a class="button refuse" style="display:inline-block;padding:5px 10px;margin:0 5px;color:#fff;background-color:#dc3545;border-radius:3px;font-size:12px;text-decoration:none;" href="{}">Refuse</a>',
            reverse('admin:refuse-user', args=[obj.pk])
        )
    refuse_button.short_description = 'Refuse'
    refuse_button.admin_order_field = 'user_cree_date'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('validate/<int:pk>/', self.admin_site.admin_view(self.validate_user), name='validate-user'),
            path('refuse/<int:pk>/', self.admin_site.admin_view(self.refuse_user), name='refuse-user'),
        ]
        return custom_urls + urls

    def validate_user(self, request, pk):
        try:
            user = User.objects.get(pk=pk, state='pending')
            # Check if DRH is trying to validate a user outside their structure
            if request.user.user_role == 'DRH' and user.structure != request.user.structure:
                self.message_user(request, "You can only validate users from your structure.", level=messages.ERROR)
                print(f"Permission denied for DRH {request.user.username}: User {user.user_username} not in structure")
                return redirect('admin:users_accountsdemanded_changelist')
            print(f"Validating user: {user.user_username} (ID: {pk})")
            user.state = 'approved'
            user.is_active = True
            if user.user_role == 'DRH':
                user.is_superuser = True
                user.is_staff = True
                print(f"User {user.user_username} set as superuser (role: drh)")
            user.save()
            Notification.objects.create(
                user=user,
                message=f"Your account has been validated. Welcome to TMS!",
            )
            self.message_user(request, f"User {user.user_username} successfully validated.")
            print(f"User {user.user_username} validated successfully")
        except User.DoesNotExist:
            self.message_user(request, "User not found or already processed.", level=messages.ERROR)
            print(f"User not found or already processed: ID {pk}")
        return redirect('admin:users_accountsdemanded_changelist')

    def refuse_user(self, request, pk):
        try:
            user = User.objects.get(pk=pk, state='pending')
            # Check if DRH is trying to refuse a user outside their structure
            if request.user.user_role == 'DRH' and user.structure != request.user.structure:
                self.message_user(request, "You can only refuse users from your structure.", level=messages.ERROR)
                print(f"Permission denied for DRH {request.user.username}: User {user.user_username} not in structure")
                return redirect('admin:users_accountsdemanded_changelist')
            print(f"Refusing user: {user.user_username} (ID: {pk})")
            user.state = 'rejected'
            user.is_active = False
            user.save()
            Notification.objects.create(
                user=user,
                message=f"Your account request has been refused.",
            )
            self.message_user(request, f"User {user.user_username} successfully refused.")
            print(f"User {user.user_username} refused successfully")
        except User.DoesNotExist:
            self.message_user(request, "User not found or already processed.", level=messages.ERROR)
            print(f"User not found or already processed: ID {pk}")
        return redirect('admin:users_accountsdemanded_changelist')

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.user_role == 'DRH'

class StructureAdmin(admin.ModelAdmin):
    list_display = ('structure_varchar', 'structure_code', 'structure_niveau', 'structure_cree_date')
    list_filter = ('structure_niveau',)
    search_fields = ('structure_varchar', 'structure_code')
    ordering = ('structure_varchar',)
    readonly_fields = ('structure_cree_par', 'structure_cree_date', 'structure_miseajour_par', 'structure_miseajour_date')

    fieldsets = (
        (None, {'fields': ('structure_varchar', 'structure_code', 'structure_niveau')}),
        ('Audit Info', {'fields': ('structure_cree_par', 'structure_cree_date', 'structure_miseajour_par', 'structure_miseajour_date')}),
    )

    def has_module_permission(self, request):
        # Only superusers who are not DRH can access the User section
        return request.user.is_superuser and request.user.user_role != 'DRH'

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'department_code', 'structure', 'department_cree_date')
    list_filter = ('structure',)
    search_fields = ('department_name', 'department_code', 'structure__structure_varchar')
    ordering = ('department_name',)
    readonly_fields = ('department_cree_par', 'department_cree_date', 'department_miseajour_par', 'department_miseajour_date')

    fieldsets = (
        (None, {'fields': ('department_name', 'department_code', 'structure')}),
        ('Audit Info', {'fields': ('department_cree_par', 'department_cree_date', 'department_miseajour_par', 'department_miseajour_date')}),
    )

    def has_module_permission(self, request):
        # Only superusers who are not DRH can access the User section
        return request.user.is_superuser and request.user.user_role != 'DRH'

class FormationAdmin(admin.ModelAdmin):
    list_display = ('formation_titre', 'formation_ref', 'formation_niveau', 'formation_cout', 'formation_pays', 'formation_category', 'structure')
    list_filter = ('formation_niveau', 'formation_pays', 'formation_category', 'structure')
    search_fields = ('formation_titre', 'formation_ref', 'structure__structure_varchar')
    ordering = ('formation_titre',)
    exclude = ('user_id',)
    readonly_fields = ('formation_mise_a_jour_cree', 'formation_mise_a_jour_date')

    fieldsets = (
        (None, {'fields': ('formation_titre', 'formation_ref', 'formation_niveau', 'formation_description', 'formation_cout', 'formation_pays', 'formation_duree', 'formation_prerequis', 'formation_programme', 'formation_cible', 'formation_objectif', 'formation_category', 'structure')}),
        ('Audit Info', {'fields': ('formation_mise_a_jour_cree', 'formation_mise_a_jour_date')}),
    )

class UserFormationAdminForm(forms.ModelForm):
    STATE_CHOICES = (
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    )
    state_formation = forms.ChoiceField(choices=STATE_CHOICES, widget=forms.Select)

    class Meta:
        model = UserFormation
        fields = '__all__'

class UserFormationAdmin(admin.ModelAdmin):
    form = UserFormationAdminForm
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'get_valide_date')
    list_filter = ('state_formation', 'date_inscription')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)
    readonly_fields = ('valide_par', 'valide_date', 'date_inscription')
    actions = ['validate_formations', 'refuse_formations']

    def get_valide_date(self, obj):
        return obj.valide_date if obj.valide_date else '-'
    get_valide_date.short_description = 'Validation Date'

    fieldsets = (
        (None, {'fields': ('user', 'formation', 'state_formation')}),
        ('Audit Info', {'fields': ('date_inscription', 'valide_par', 'valide_date')}),
    )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'state_formation':
            kwargs['choices'] = (
                ('approved', 'Approved'),
                ('pending', 'Pending'),
                ('rejected', 'Rejected'),
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def validate_formations(self, request, queryset):
        updated = queryset.filter(state_formation='pending').update(
            state_formation='approved',
            valide_par=request.user,
            valide_date=timezone.now()
        )
        for user_formation in queryset.filter(state_formation='pending'):
            Notification.objects.create(
                user=user_formation.user,
                message=f"Your registration for '{user_formation.formation.formation_titre}' has been validated."
            )
        self.message_user(request, f"{updated} formation registration(s) successfully validated.")
    validate_formations.short_description = "Validate selected formations"

    def refuse_formations(self, request, queryset):
        updated = queryset.filter(state_formation='pending').update(
            state_formation='rejected',
            valide_par=request.user,
            valide_date=timezone.now()
        )
        for user_formation in queryset.filter(state_formation='pending'):
            Notification.objects.create(
                user=user_formation.user,
                message=f"Your registration for '{user_formation.formation.formation_titre}' has been refused."
            )
        self.message_user(request, f"{updated} formation registration(s) successfully refused.")
    refuse_formations.short_description = "Refuse selected formations"

class PendingUserFormationsAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'get_valide_date', 'validate_button', 'refuse_button')
    list_filter = ('state_formation', 'date_inscription', 'formation__structure')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)
    readonly_fields = ('user', 'formation', 'date_inscription', 'valide_par', 'valide_date')

    def get_queryset(self, request):
        qs = UserFormation.objects.filter(state_formation='pending')
        if request.user.is_superuser and request.user.user_role != 'DRH':
            # Admins (non-DRH superusers) can see all pending formation registrations
            return qs
        elif request.user.user_role == 'DRH' and request.user.structure:
            # DRH users can only see pending formations from their structure
            return qs.filter(formation__structure=request.user.structure)
        return qs.none()  # Return empty queryset if user has no structure or invalid role

    def get_valide_date(self, obj):
        return obj.valide_date if obj.valide_date else '-'
    get_valide_date.short_description = 'Validation Date'

    def validate_button(self, obj):
        return format_html(
            '<a class="button validate" style="display:inline-block;padding:5px 10px;margin:0 5px;color:#fff;background-color:#28a745;border-radius:3px;font-size:12px;text-decoration:none;" href="{}">Validate</a>',
            reverse('admin:validate-user-formation', args=[obj.pk])
        )
    validate_button.short_description = 'Validate'
    validate_button.admin_order_field = 'date_inscription'

    def refuse_button(self, obj):
        return format_html(
            '<a class="button refuse" style="display:inline-block;padding:5px 10px;margin:0 5px;color:#fff;background-color:#dc3545;border-radius:3px;font-size:12px;text-decoration:none;" href="{}">Refuse</a>',
            reverse('admin:refuse-user-formation', args=[obj.pk])
        )
    refuse_button.short_description = 'Refuse'
    refuse_button.admin_order_field = 'date_inscription'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('validate-formation/<int:pk>/', self.admin_site.admin_view(self.validate_user_formation), name='validate-user-formation'),
            path('refuse-formation/<int:pk>/', self.admin_site.admin_view(self.refuse_user_formation), name='refuse-user-formation'),
        ]
        return custom_urls + urls

    def validate_user_formation(self, request, pk):
        try:
            user_formation = UserFormation.objects.get(pk=pk, state_formation='pending')
            # Check if DRH is trying to validate a formation outside their structure
            if request.user.user_role == 'DRH' and user_formation.formation.structure != request.user.structure:
                self.message_user(request, "You can only validate formations from your structure.", level=messages.ERROR)
                print(f"Permission denied for DRH {request.user.username}: Formation {user_formation.formation.formation_titre} not in structure")
                return redirect('admin:users_pendinguserformations_changelist')
            print(f"Validating formation for user: {user_formation.user.user_username}, formation: {user_formation.formation.formation_titre} (ID: {pk})")
            user_formation.state_formation = 'approved'
            user_formation.valide_date = timezone.now()
            user_formation.save()
            Notification.objects.create(
                user=user_formation.user,
                message=f"Your registration for '{user_formation.formation.formation_titre}' has been validated."
            )
            self.message_user(request, f"Formation registration for {user_formation.user.user_username} successfully validated.")
            print(f"Formation registration validated successfully for user: {user_formation.user.user_username}")
        except UserFormation.DoesNotExist:
            self.message_user(request, "Formation registration not found or already processed.", level=messages.ERROR)
            print(f"Formation registration not found or already processed: ID {pk}")
        return redirect('admin:users_pendinguserformations_changelist')

    def refuse_user_formation(self, request, pk):
        try:
            user_formation = UserFormation.objects.get(pk=pk, state_formation='pending')
            # Check if DRH is trying to refuse a formation outside their structure
            if request.user.user_role == 'DRH' and user_formation.formation.structure != request.user.structure:
                self.message_user(request, "You can only refuse formations from your structure.", level=messages.ERROR)
                print(f"Permission denied for DRH {request.user.username}: Formation {user_formation.formation.formation_titre} not in structure")
                return redirect('admin:users_pendinguserformations_changelist')
            print(f"Refusing formation for user: {user_formation.user.user_username}, formation: {user_formation.formation.formation_titre} (ID: {pk})")
            user_formation.state_formation = 'rejected'
            user_formation.valide_par = request.user.user_id
            user_formation.valide_date = timezone.now()
            user_formation.save()
            Notification.objects.create(
                user=user_formation.user,
                message=f"Your registration for '{user_formation.formation.formation_titre}' has been refused."
            )
            self.message_user(request, f"Formation registration for {user_formation.user.user_username} successfully refused.")
            print(f"Formation registration refused successfully for user: {user_formation.user.user_username}")
        except UserFormation.DoesNotExist:
            self.message_user(request, "Formation registration not found or already processed.", level=messages.ERROR)
            print(f"Formation registration not found or already processed: ID {pk}")
        return redirect('admin:users_pendinguserformations_changelist')

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.user_role == 'DRH'

# Register models
admin.site.register(User, UserAdmin)
admin.site.register(Structure, StructureAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(UserFormation, UserFormationAdmin)

# Register Accounts Demanded as a proxy model
class AccountsDemanded(User):
    class Meta:
        proxy = True
        verbose_name = "Account Demanded"
        verbose_name_plural = "Accounts Demanded"

admin.site.register(AccountsDemanded, AccountsDemandedAdmin)

# Register Pending User Formations as a proxy model
class PendingUserFormations(UserFormation):
    class Meta:
        proxy = True
        verbose_name = "Pending Formation Registration"
        verbose_name_plural = "Pending Formation Registrations"

admin.site.register(PendingUserFormations, PendingUserFormationsAdmin)