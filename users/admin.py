from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_admin', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_admin', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (ProfileInline,)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'newsletter', 'created_at')
    list_filter = ('newsletter', 'created_at')
    search_fields = ('user__email', 'phone', 'address')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations de contact', {
            'fields': ('phone', 'address')
        }),
        ('Préférences', {
            'fields': ('newsletter',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )