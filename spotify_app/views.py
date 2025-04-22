from django.http import HttpResponse
from django.shortcuts import render

from .models import Song,Musician

def index(request):
   return HttpResponse("Hello, world. You're at the application index.")

def song_list(request):
   songs = Song.objects.all()
   return render(request, "song_list.html", {"songs": songs})

def musician_list(request):
   musicians = Musician.objects.all()
   return render(request, "musician_list.html", {"musicians": musicians})