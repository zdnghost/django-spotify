from rest_framework import serializers
from .models import Musician, Album, Song, Playlist, Account, UserFavorite
from django.db.models import Q
from spotify_users.models import UserFollow

class MusicianSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    class Meta:
        model = Musician
        fields =  ('musician_name','introduce','social_media', 'number_of_follower', 'is_followed')
    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.objects.filter(user=request.user, musician=obj).exists()
        return False

class AlbumSerializer(serializers.ModelSerializer):
    musicians = MusicianSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ('album_name','musicians')

class SongSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Song
        fields = ['id', 'title', 'song_file', 'duration']
    
    def get_id(self, obj):
        return str(obj.id)

class MusicianListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Musician
        fields = ['id', 'musician_name']
    
    def get_id(self, obj):
        return str(obj.id)

class PlaylistSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    songs = SongSerializer(many=True, read_only=True)
    musicians = MusicianListSerializer(many=True, read_only=True)
    song_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'user_id', 'playlist_name', 'description', 'created_at', 'updated_at', 
                  'is_public', 'cover_image', 'songs', 'musicians', 'song_count']
    
    def get_id(self, obj):
        return str(obj.id)  # Convert ObjectId to string
    
    def get_user_id(self, obj):
        if obj.user:
            return str(obj.user.id)  # Convert ObjectId to string
        return None
    
    def get_song_count(self, obj):
        try:
            return obj.songs.count()
        except AttributeError:
            return 0

class PlaylistCreateSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    class Meta:
        model = Playlist
        fields = ('playlist_name', 'description', 'is_public', 'cover_image')
    
    def create(self, validated_data):
        user = self.context['request'].user
        playlist = Playlist.objects.create(user=user, **validated_data)
        return playlist

class PlaylistSongActionSerializer(serializers.Serializer):
    song_id = serializers.CharField(required=True)

class UserFavoriteSerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ('id', 'song', 'favorited_at')
        read_only_fields = ('id', 'favorited_at')

class UserFavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ('song',)
    
    def create(self, validated_data):
        user = self.context['request'].user
        song = validated_data.get('song')
        
        # kiểm tra nếu favorite đã tồn tại
        favorite, created = UserFavorite.objects.get_or_create(
            user=user,
            song=song
        )
        return favorite

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
            Q(title__icontains=query) | 
            Q(musicians__musician_name__icontains=query) | 
            Q(album__album_name__icontains=query)
        ).distinct()
        songs_data = SongSerializer(songs, many=True).data
        
        # Tìm kiếm playlists
        playlists = Playlist.objects.filter(
            Q(playlist_name__icontains=query) | 
            Q(musicians__musician_name__icontains=query) | 
            Q(songs__title__icontains=query)
        ).distinct()
        playlists_data = PlaylistSerializer(playlists, many=True).data
        
        return {
            'musicians': musicians_data,
            'albums': albums_data,
            'songs': songs_data,
            'playlists': playlists_data
        }