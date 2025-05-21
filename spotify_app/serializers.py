from rest_framework import serializers
from .models import Musician, Album, Song, Playlist, Account, UserFavorite
from django.db.models import Q
from spotify_users.models import UserFollow

class MusicianSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    avatar_pic = serializers.ImageField()
    cover_pic = serializers.ImageField()

    class Meta:
        model = Musician
        fields = ('id', 'musician_name','avatar_pic','cover_pic', 'about', 'social_media','is_verified', 'number_of_follower', 'is_followed')
    
    def get_id(self, obj):
        return str(obj.id)
        
    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFollow.objects.filter(user=request.user, musician=obj).exists()
        return False

class SongSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    albumArt = serializers.ImageField()
    musicians = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    musicians = serializers.SerializerMethodField()
    day_add = serializers.DateField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'albumArt', 'duration', 'musicians', 'views', 'album', 'day_add']
    
    def get_id(self, obj):
        return str(obj.id)
    
    def get_musicians(self, obj):
        try:
            return MusicianListSerializer(obj.musicians.all(), many=True, context=self.context).data
        except Exception:
            
            return None
            
    def get_album(self, obj):
        try:
            if obj.album:
                return {
                    'id': str(obj.album.id),
                    'album_name': obj.album.album_name
                }
            return None
        except Exception:
            return None

class AlbumSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    coverurl = serializers.ImageField()

    class Meta:
        model = Album
        fields = ['id', 'album_name', 'coverurl', 'day_add', 'songs']

    def get_songs(self, obj):
        return SongSerializer(obj.song_set.all(), many=True).data     
    
    def get_id(self, obj):
        return str(obj.id)

class MusicianListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    avatar_pic = serializers.ImageField()

    class Meta:
        model = Musician
        fields = ['id', 'musician_name','avatar_pic']
    
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
        fields = ('id', 'playlist_name', 'description', 'is_public', 'cover_image')
    
    def get_id(self, obj):
        return str(obj.id)
        
    def create(self, validated_data):
        user = self.context['request'].user
        playlist = Playlist.objects.create(user=user, **validated_data)
        return playlist

class FavoriteToggleSerializer(serializers.Serializer):
    song_id = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all())

class UserFavoriteSerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)
    id = serializers.SerializerMethodField()

    class Meta:
        model = UserFavorite
        fields = ('id', 'song', 'favorited_at')
        read_only_fields = ('id', 'favorited_at')
    def get_id(self, obj):
        if hasattr(obj, 'id'):
            return str(obj.id)  # Convert ObjectId to string
        return None

class UserFavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = ('song',)
    
    def create(self, validated_data):
        user = self.context['request'].user
        song = validated_data.get('song')
        
        
        favorite, created = UserFavorite.objects.get_or_create(
            user=user,
            song=song
        )
        return favorite

class AccountSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 
                  'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        
    def get_id(self, obj):
        return str(obj.id)

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
        musicians_data = MusicianSerializer(musicians, many=True, context=self.context).data
        
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
        playlists_data = PlaylistSerializer(playlists, many=True, context=self.context).data
        
        return {
            'musicians': musicians_data,
            'albums': albums_data,
            'songs': songs_data,
            'playlists': playlists_data
        }