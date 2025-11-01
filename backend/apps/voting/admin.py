"""
Админ-панель для голосования
"""

from django.contrib import admin
from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        'session', 'voter', 'target', 'score', 'modified_by_admin', 'created_at'
    )
    list_filter = ('score', 'modified_by_admin', 'session', 'created_at')
    search_fields = (
        'voter__first_name', 'voter__last_name',
        'target__first_name', 'target__last_name'
    )
    raw_id_fields = ('session', 'voter', 'target')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'voter', 'target')