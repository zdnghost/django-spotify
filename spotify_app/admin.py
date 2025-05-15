from django.contrib import admin

# Register your models here.
from .models import Song,Musician,Album,Playlist,Account

admin.site.register(Song)

admin.site.register(Musician)
admin.site.register(Playlist)
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['album_name','get_musicians']
    def get_musicians(self, obj):
        return ", ".join([musician.musician_name for musician in obj.musicians.all()])
    
    get_musicians.short_description = 'Musicians'
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'date_joined']
    list_filter = ['role']
    search_fields = ['username', 'email']
