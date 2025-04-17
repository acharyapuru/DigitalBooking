from django.contrib import admin
from user.models import User, UserProfile
from .froms import UserForm, UserCustomCreationForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    form = UserForm
    add_form = UserCustomCreationForm
    list_display = ['email', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'is_superuser']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions'
            )},
        ),
    )
    readonly_fields = ['last_login', 'date_joined']

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ['email', 'phone', 'address']
    list_filter = ['email', 'phone', 'address']
    search_fields = ['email', 'phone', 'address']
    ordering = ['email']
