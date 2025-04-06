from django.contrib import admin

# Register your models here.
from .models import UserActivityLog  

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_quiz', 'big_quiz', 'lessons_watched')
    raw_id_fields = ('user',)