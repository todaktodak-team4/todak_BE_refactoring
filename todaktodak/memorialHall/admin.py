from django.contrib import admin
from .models import MemorialHall, Wreath, Message
# MemorialHall 모델의 관리자 페이지
class MemorialHallAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'approved', 'public', 'private', 'token']
    list_filter = ['approved', 'public', 'private', 'date']
    search_fields = ['name', 'info']
    actions = ['approve_halls']

    def approve_halls(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected memorial halls have been approved.")
    approve_halls.short_description = "Approve selected memorial halls"
    
admin.site.register(MemorialHall, MemorialHallAdmin)
admin.site.register(Wreath)
admin.site.register(Message)
