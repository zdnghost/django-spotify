from rest_framework import serializers
from .models import Musician, Album, Song, Playlist, Account
from django.db.models import Q

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
        fields = ['id', 'username', 'email', 
                  'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class SearchResultSerializer(serializers.Serializer):
    musicians = MusicianSerializer(many=True, read_only=True)
    albums = AlbumSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    playlists = PlaylistSerializer(many=True, read_only=True)
    
    def to_representation(self, instance):
        query = instance.get('query', '')
        
        if not query:
            return {
                'musicians': [],
                'albums': [],
                'songs': [],
                'playlists': []
            }
        
        # Tìm kiếm musicians
        musicians = Musician.objects.filter(musician_name__icontains=query)
        musicians_data = MusicianSerializer(musicians, many=True).data
        
        # Tìm kiếm albums
        albums = Album.objects.filter(album_name__icontains=query)
        albums_data = AlbumSerializer(albums, many=True).data
        
        # Tìm kiếm songs
        songs = Song.objects.filter(
            Q(song_name__icontains=query) | 
            Q(musicians__musician_name__icontains=query) | 
            Q(album__album_name__icontains=query)
        ).distinct()
        songs_data = SongSerializer(songs, many=True).data
        
        # Tìm kiếm playlists
        playlists = Playlist.objects.filter(
            Q(playlist_name__icontains=query) | 
            Q(musicians__musician_name__icontains=query) | 
            Q(songs__song_name__icontains=query)
        ).distinct()
        playlists_data = PlaylistSerializer(playlists, many=True).data
        
        return {
            'musicians': musicians_data,
            'albums': albums_data,
            'songs': songs_data,
            'playlists': playlists_data
        }