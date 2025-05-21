from django.http import HttpResponse ,Http404 ,StreamingHttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status, generics, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .serializers import MusicianSerializer, AlbumSerializer, SongSerializer, PlaylistSerializer, AccountSerializer, SearchResultSerializer, PlaylistCreateSerializer, PlaylistSongActionSerializer, UserFavoriteSerializer, UserFavoriteCreateSerializer
from .models import Musician, Album, Song, Playlist, Account, UserFavorite
import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv
from .models import Song,Musician
from pathlib import Path
from bson import ObjectId
from django.db.models import F, Q
from spotify_users.models import UserFollow

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

def index(request):
   return HttpResponse("Hello, world. You're at the application index.")

class IsPlaylistOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # chỉ người sở hữu mới có quyền
        return obj.user == request.user
    
class MusicianViewSet(viewsets.ModelViewSet):
    queryset = Musician.objects.all()
    serializer_class = MusicianSerializer
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        musician = self.get_object()
        user = request.user
        
        # kiểm tra có follow chưa
        follow_exists = UserFollow.objects.filter(user=user, musician=musician).exists()
        
        if follow_exists:
            return Response({"detail": "You are already following this musician."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        
        UserFollow.objects.create(user=user, musician=musician)
        
        
        Musician.objects.filter(id=musician.id).update(number_of_follower=F('number_of_follower') + 1)
        
        return Response({"detail": f"You are now following {musician.musician_name}."}, 
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        musician = self.get_object()
        user = request.user
        

        try:
            follow = UserFollow.objects.get(user=user, musician=musician)
        except UserFollow.DoesNotExist:
            return Response({"detail": "You are not following this musician."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        

        follow.delete()
        

        Musician.objects.filter(id=musician.id).update(number_of_follower=F('number_of_follower') - 1)
        
        return Response({"detail": f"You have unfollowed {musician.musician_name}."}, 
                       status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request):
        
        user = request.user
        followed_musician_ids = UserFollow.objects.filter(user=user).values_list('musician_id', flat=True)
        followed_musicians = Musician.objects.filter(id__in=followed_musician_ids)
        
        serializer = self.get_serializer(followed_musicians, many=True)
        return Response(serializer.data)

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class AlbumDetailView(APIView):
    def get(self, request, pk):
        album = Album.objects.get(pk=pk)
        serializer = AlbumSerializer(album)
        return Response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.filter(is_public=True)
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class UserPlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Playlist.objects.none()
        

        return Playlist.objects.filter(
            Q(user=user) | Q(is_public=True)
        ).distinct()
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Song ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            song = Song.objects.get(id=song_id)
            playlist.songs.add(song)
            return Response({
                'message': 'Song added to playlist successfully!',
                'playlist': PlaylistSerializer(playlist, context={'request': request}).data
            })
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get('song_id')

        if not song_id:
            return Response({'error': 'Song ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            song = Song.objects.get(id=song_id)
            playlist.songs.remove(song)
            return Response({
                'message': 'Song removed from playlist successfully!',
                'playlist': PlaylistSerializer(playlist, context={'request': request}).data
            })
        except Song.DoesNotExist:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)
    
class UserFavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserFavoriteCreateSerializer
        return UserFavoriteSerializer
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.song.title
        self.perform_destroy(instance)
        return Response({"detail": f"Song '{title}' removed from favorites."}, 
                      status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        serializer = UserFavoriteCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            song = serializer.validated_data['song']
            user = request.user
            
            try:
                
                favorite = UserFavorite.objects.get(user=user, song=song)
                
                favorite.delete()
                return Response({"detail": f"Song '{song.title}' removed from favorites.",
                                "is_favorite": False}, 
                              status=status.HTTP_200_OK)
            except UserFavorite.DoesNotExist:
                # nếu không có thì favorited
                UserFavorite.objects.create(user=user, song=song)
                return Response({"detail": f"Song '{song.title}' added to favorites.",
                                "is_favorite": True}, 
                              status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

def stream_song(request, song_id):
    try:
        song_obj_id = ObjectId(song_id)  
    except Exception:
        raise Http404("ID không hợp lệ")

    try:
        song = Song.objects.get(id=song_obj_id)
    except Song.DoesNotExist:
        raise Http404("Bài hát không tồn tại")

    # Tăng lượt nghe
    Song.objects.filter(id=song_obj_id).update(views=F('views') + 1)

    # Stream file từ S3
    bucket_name = AWS_STORAGE_BUCKET_NAME
    object_key = song.song_file.name  # ví dụ: "song_files/audio.mp3"

    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME,
        config=Config(signature_version='s3v4')
    )

    s3_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    response = StreamingHttpResponse(
        streaming_content=s3_object['Body'].iter_chunks(),
        content_type='audio/mpeg'
    )
    response['Content-Disposition'] = f'inline; filename="{song.title}.mp3"'
    return response

def stream_video(request, song_id):
    try:
        song_obj_id = ObjectId(song_id)  
    except Exception:
        raise Http404("ID không hợp lệ")

    try:
        song = Song.objects.get(id=song_obj_id)
    except Song.DoesNotExist:
        raise Http404("Bài hát không tồn tại")

    # Tăng lượt nghe
    Song.objects.filter(id=song_obj_id).update(views=F('views') + 1)

    # Stream file từ S3
    bucket_name = AWS_STORAGE_BUCKET_NAME
    object_key = song.video_file.name  # ví dụ: "video_files/audio.mp4"

    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME,
        config=Config(signature_version='s3v4')
    )

    s3_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    response = StreamingHttpResponse(
        streaming_content=s3_object['Body'].iter_chunks(),
        content_type='video/mp4'
    )
    response['Content-Disposition'] = f'inline; filename="{song.title}.mp4"'
    return response

class SearchView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SearchResultSerializer
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {"message": "Vui lòng cung cấp từ khóa tìm kiếm."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer({'query': query})
        return Response(serializer.data)