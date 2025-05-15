from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import EmbeddedModelField, ArrayField
from django_mongodb_backend.models import EmbeddedModel


class Musician(models.Model):
    musician_name = models.CharField(max_length=255)
    number_of_follower = models.IntegerField(default=0)
    introduce = models.TextField(blank=True)
    is_followed = models.BooleanField(default=False)
    # Dạng dictionary chứa các link mạng xã hội
    social_media = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "musician"
        managed = False

    def __str__(self):
        if self.musician_name is None:
            return "Musician name is None"
        return self.musician_name

class Album(models.Model):
    album_name = models.CharField(max_length=255)
    coverurl = models.ImageField(upload_to='album_pictures/')
    musicians = models.ManyToManyField(Musician, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = "album"
        managed = False

    def __str__(self):
        return self.album_name

class Song(models.Model):
    title = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    albumArt = models.ImageField(upload_to='song_pictures/')
    song_file = models.FileField(upload_to='song_files/')
    video_file = models.FileField(upload_to='video_files/', blank=True)
    musicians = models.ManyToManyField(Musician, blank=True)

    day_add = models.DateField()
    views = models.IntegerField(default=0)  

    album =models.ForeignKey(Album, null=True, blank=True, on_delete=models.SET_NULL)


    class Meta:
        db_table = "song"
        managed = False

    def __str__(self):
        if self.title is None:
            return "Song title is None"
        return self.title

class Playlist(models.Model):
    playlist_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='playlists', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', null=True, blank=True)
    
    musicians = models.ManyToManyField(Musician, blank=True)
    songs = models.ManyToManyField(Song, blank=True)

    class Meta:
        db_table = "playlist"
        managed = False

    def __str__(self):
        return self.playlist_name

class UserFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorited_by')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_favorites"
        managed = False
        unique_together = ('user', 'song')  

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.song.title}"

class Account(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.BooleanField()  # True: Male, False: Female
    birthday = models.DateField()
    role = models.CharField(max_length=50, default="staff")  # e.g., admin, staff, manager
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_account"
        managed = False

    def __str__(self):
        return self.username


