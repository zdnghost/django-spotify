from rest_framework import serializers
from .models import Musician, Album, Song, Playlist, Account
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
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
    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                msg = _('Đăng nhập không thành công.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Vui lòng nhập email và mật khẩu.')
            raise serializers.ValidationError(msg, code='authorization')
        
        data['user'] = user
        return data
    
    class RegisterSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
        password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
        
        class Meta:
            model = Account
            fields = ['email', 'user_name', 'password', 'password2', 'gender', 'birthday']
        
        def validate(self, data):
            if data['password'] != data['password2']:
                raise serializers.ValidationError({"password": "Mật khẩu không khớp."})
            return data
        
        def create(self, validated_data):
            validated_data.pop('password2')
            password = validated_data.pop('password')
            user = Account.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            return user

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
            
            # Tìm kiếm musician
            musicians = Musician.objects.filter(musician_name__icontains=query)
            musicians_data = MusicianSerializer(musicians, many=True).data
            
            # Tìm kiếm album
            albums = Album.objects.filter(album_name__icontains=query)
            albums_data = AlbumSerializer(albums, many=True).data
            
            # Tìm kiếm song
            songs = Song.objects.filter(
                Q(song_name__icontains=query) | 
                Q(musicians__musician_name__icontains=query) | 
                Q(album__album_name__icontains=query)
            ).distinct()
            songs_data = SongSerializer(songs, many=True).data
            
            # Tìm kiếm playlist
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