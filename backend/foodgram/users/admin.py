from django.contrib import admin

from .models import Follow, User

admin.site.register(User)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Follow)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user')
    list_editable = ('author', 'user')
