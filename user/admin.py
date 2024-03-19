from django.contrib.admin import register, ModelAdmin

from user.models import User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ['email', 'username', 'last_login', 'date_joined']
    ordering = ['-date_joined']
    exclude = ['password']
