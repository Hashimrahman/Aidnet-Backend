from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')  
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name') 
    ordering = ('email',) 
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'organization_name', 'skills')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'role')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),  
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'organization_name', 'skills')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'role')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class CustomGroupAdmin(GroupAdmin):
    def users_in_group(self, obj):
        return ", ".join([user.email for user in obj.user_set.all()]) 

    users_in_group.short_description = "Users"
    list_display = ("name", "users_in_group") 
    search_fields = ("name",)

admin.site.unregister(Group) 
admin.site.register(Group, CustomGroupAdmin) 
