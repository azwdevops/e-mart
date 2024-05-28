from django.contrib.admin import register, ModelAdmin
from django.utils.html import format_html

from user.models import User


@register(User)
class UserAdmin(ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture:
            return format_html(f'<img src="{object.profile_picture.url}" width="30" height="30" style="border-radius:50%;" />')
    thumbnail.short_description = 'Profile Photo'
    list_display = ['email', 'username',
                    'last_login', 'date_joined', 'thumbnail']
    ordering = ['-date_joined']
    exclude = ['password']
