from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import MusicianSerializer, AlbumSerializer, SongSerializer, PlaylistSerializer, AccountSerializer
from .models import Musician, Album, Song, Playlist, Account

from .models import Song,Musician

def index(request):
   return HttpResponse("Hello, world. You're at the application index.")


class MusicianViewSet(viewsets.ModelViewSet):
    queryset = Musician.objects.all()
    serializer_class = MusicianSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer