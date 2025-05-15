from django.http import HttpResponse ,Http404 ,StreamingHttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import MusicianSerializer, AlbumSerializer, SongSerializer, PlaylistSerializer, AccountSerializer, SearchResultSerializer
from .models import Musician, Album, Song, Playlist, Account
import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv
from .models import Song,Musician
from pathlib import Path
from bson import ObjectId
from django.db.models import F
from spotify_users.models import UserFollow

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

def index(request):
   return HttpResponse("Hello, world. You're at the application index.")


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
        
        # Check if already following
        follow_exists = UserFollow.objects.filter(user=user, musician=musician).exists()
        
        if follow_exists:
            return Response({"detail": "You are already following this musician."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Create the follow relationship
        UserFollow.objects.create(user=user, musician=musician)
        
        # Increment the follower count
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

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

def stream_song(request, song_id):
    try:
        song_obj_id = ObjectId(song_id)  # Chuyển từ chuỗi sang ObjectId
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
    response['Content-Disposition'] = f'inline; filename="{song.song_name}.mp3"'
    return response

def stream_video(request, song_id):
    try:
        song_obj_id = ObjectId(song_id)  # Chuyển từ chuỗi sang ObjectId
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
    object_key = song.video_file.name  # ví dụ: "song_files/audio.mp3"

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
    response['Content-Disposition'] = f'inline; filename="{song.song_name}.mp4"'
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