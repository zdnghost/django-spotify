from django.http import HttpResponse ,Http404 ,StreamingHttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import MusicianSerializer, AlbumSerializer, SongSerializer, PlaylistSerializer, AccountSerializer
from .models import Musician, Album, Song, Playlist, Account
import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv
from .models import Song,Musician
from pathlib import Path
from bson import ObjectId
from django.db.models import F

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
    print(f"Incrementing views for song {song_id} by {increment}")
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