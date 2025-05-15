from django.contrib import admin

# Register your models here.
from .models import Song,Musician,Album,Playlist

admin.site.register(Song)

admin.site.register(Musician)
admin.site.register(Playlist)
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['album_name','get_musicians']
    def get_musicians(self, obj):
        return ", ".join([musician.musician_name for musician in obj.musicians.all()])
    
    get_musicians.short_description = 'Musicians'


