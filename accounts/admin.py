from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from .models import CustomUser, LawyerProfile

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('full_name', 'phone')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'password1', 'password2', 'is_staff'),
        }),
    )
    list_display = ('email', 'full_name', 'phone', 'is_staff')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('email',)

class LawyerProfileAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.resolver_match and request.resolver_match.kwargs.get('object_id'):
                # Редактирование существующего объекта
                object_id = request.resolver_match.kwargs.get('object_id')
                try:
                    obj = self.model.objects.get(pk=object_id)
                    kwargs["queryset"] = CustomUser.objects.filter(
                        models.Q(lawyerprofile__isnull=True) | models.Q(pk=obj.user.pk)
                    )
                except self.model.DoesNotExist:
                    kwargs["queryset"] = CustomUser.objects.filter(lawyerprofile__isnull=True)
            else:
                # Создание нового объекта
                kwargs["queryset"] = CustomUser.objects.filter(lawyerprofile__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ['user', 'id']
    search_fields = ['user__email']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LawyerProfile, LawyerProfileAdmin)