from rest_framework import serializers
from .models import Musician, Album, Song, Playlist, Account

class MusicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musician
        fields =  ('musician_name','introduce','social_media')

class AlbumSerializer(serializers.ModelSerializer):
    musicians = MusicianSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ('album_name','musicians')

class SongSerializer(serializers.ModelSerializer):  
    musicians = MusicianSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Song
        fields = ('song_name','song_picture','song_file','album','musicians')

class PlaylistSerializer(serializers.ModelSerializer):
    musicians = MusicianSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
