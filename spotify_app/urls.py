from django.urls import path

from . import views

urlpatterns = [
   path("song_list/", views.song_list, name="song_list"),
   path("musician_list/", views.musician_list, name="musician_list"),
   path("", views.index, name="index")
]
