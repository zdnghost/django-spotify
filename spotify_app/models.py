from django.db import models
from django.conf import settings
from django_mongodb_backend.fields import EmbeddedModelField, ArrayField
from django_mongodb_backend.models import EmbeddedModel
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
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

    musicians = models.ManyToManyField(Musician, blank=True)

    class Meta:
        db_table = "album"
        managed = False

    def __str__(self):
        return self.album_name

class Song(models.Model):
    song_name = models.CharField(max_length=255)

    song_picture = models.FileField(upload_to='song_pictures/')
    song_file = models.FileField(upload_to='song_files/')

    musicians = models.ManyToManyField(Musician, blank=True)

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

    musicians = models.ManyToManyField(Musician, blank=True)
    songs = models.ManyToManyField(Song, blank=True)

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

    class Meta:
        db_table = "account"
        managed = False

    def __str__(self):
        return self.user_name

class AccountUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=255, unique=True)
    gender = models.BooleanField(null=True, blank=True)  # True: Nam, False: Nữ
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Thêm các trường liên quan đến playlist yêu thích và nghệ sĩ yêu thích
    favorite_playlists = models.ManyToManyField('Playlist', blank=True, related_name='favorited_by')
    favorite_musicians = models.ManyToManyField('Musician', blank=True, related_name='fans')
    favorite_songs = models.ManyToManyField('Song', blank=True, related_name='liked_by')
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='',  
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='',
        blank=True,
    )

    class Meta:
        db_table = "account"
        managed = False

    def __str__(self):
        return self.user_name


