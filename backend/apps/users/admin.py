"""
Админ-панель для пользователей
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Отображение в списке
    list_display = (
        'username', 'get_display_name', 'role', 'status', 
        'telegram_id', 'can_vote', 'can_receive_votes', 'last_login'
    )
    list_filter = ('role', 'status', 'can_vote', 'can_receive_votes', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'telegram_username', 'email')
    
    # Поля для редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name', 'middle_name', 'email')
        }),
        ('Telegram', {
            'fields': ('telegram_id', 'telegram_username')
        }),
        ('Рабочая информация', {
            'fields': ('position', 'department', 'role', 'status')
        }),
        ('Права голосования', {
            'fields': ('can_vote', 'can_receive_votes')
        }),
        ('Административные', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined', 'last_vote_date')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'first_name', 'last_name',
                'telegram_id', 'role', 'email'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'last_vote_date', 'created_at', 'updated_at')
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Полное имя'