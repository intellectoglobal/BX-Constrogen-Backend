from django.contrib import admin
from users.models import AppUser, AppRole, AppPermission, AppRolePermission, AppUsersRole, Authentication, UserSettings
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models


class UserAdminConfig(UserAdmin):
    model = AppUser
    search_fields = ('email', 'user_name', 'first_name', 'phone_number')
    list_filter = ('email', 'user_name', 'first_name',
                   'last_name', 'phone_number')
    ordering = ('-start_date',)
    list_display = ('email', 'user_name', 'first_name',
                    'last_name', 'phone_number', 'profile_pic')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'profile_pic',),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'user_name',
         'first_name', 'last_name', 'phone_number', 'profile_pic',)}),
        ('Permissions', { 'fields': ()}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }


admin.site.register(AppUser, UserAdminConfig)
admin.site.register(AppRole)
admin.site.register(AppPermission)
admin.site.register(AppRolePermission)
admin.site.register(AppUsersRole)
admin.site.register(Authentication)
admin.site.register(UserSettings)
