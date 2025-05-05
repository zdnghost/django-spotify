from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import EmbeddedModelField, ArrayField
from django_mongodb_backend.models import EmbeddedModel

# Create your models here.
class Musician(models.Model):
    musician_name = models.CharField(max_length=255)
    number_of_follower = models.IntegerField(default=0)
    introduce = models.TextField(blank=True)

    # Dạng dictionary chứa các link mạng xã hội
    social_media = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "musician"
        managed = False

    def __str__(self):
        return self.musician_name

class Album(models.Model):
    album_name = models.CharField(max_length=255)

    musicians = models.ManyToManyField(Musician, blank=True, null=True)

    class Meta:
        db_table = "album"
        managed = False

    def __str__(self):
        return self.album_name

class Song(models.Model):
    song_name = models.CharField(max_length=255)

    song_picture = models.ImageField(upload_to='song_pictures/')
    song_file = models.FileField(upload_to='song_files/')

    musicians = models.ManyToManyField(Musician, blank=True, null=True)

    day_add = models.DateField()
    views = models.IntegerField(default=0)  

    album =models.ForeignKey(Album, null=True, blank=True, on_delete=models.SET_NULL)


    class Meta:
        db_table = "song"
        managed = False

    def __str__(self):
        return self.song_name

class Playlist(models.Model):
    playlist_name = models.CharField(max_length=255)

    musicians = models.ManyToManyField(Musician, blank=True, null=True)
    songs = models.ManyToManyField(Song, blank=True, null=True)

    class Meta:
        db_table = "playlist"
        managed = False

    def __str__(self):
        return self.playlist_name

class Account(models.Model):
    user_name = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.BooleanField()  # True: Nam, False: Nữ
    birthday = models.DateField()
    region = models.CharField(max_length=100)

    class Meta:
        db_table = "account"
        managed = False

    def __str__(self):
        return self.user_name



