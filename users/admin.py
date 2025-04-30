from django.contrib import admin
from .models import User, Structure, Department, Formation, UserFormation, Notification
from django.contrib.auth import logout  # Reintroduce for logout
from django.contrib import messages
from django.shortcuts import redirect, render


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
    readonly_fields = ('user_cree_date', 'user_miseajour_date')

    fieldsets = (
        (None, {'fields': ('user_email', 'user_username', 'user_firstname', 'user_lastname')}),
        ('Details', {'fields': ('user_role', 'structure', 'department', 'state')}),
        ('Audit Info', {'fields': ('user_cree_par', 'user_miseajour_par', 'user_miseajour_date')}),
    )

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
    list_display = ('user', 'formation', 'date_inscription', 'state_formation', 'get_valide_date')
    list_filter = ('state_formation', 'date_inscription')
    search_fields = ('user__user_username', 'formation__formation_titre')
    ordering = ('date_inscription',)

    def get_valide_date(self, obj):
        return obj.valide_date if obj.valide_date else '-'
    get_valide_date.short_description = 'Validation Date'

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