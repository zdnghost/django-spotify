from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MusicianViewSet, AlbumViewSet, SongViewSet, PlaylistViewSet, AccountViewSet, stream_song, stream_video, SearchView, UserPlaylistViewSet, UserFavoriteViewSet
router = DefaultRouter()
router.register(r'musicians', MusicianViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'songs', SongViewSet)
router.register(r'playlists', PlaylistViewSet)
router.register(r'admin-accounts', AccountViewSet)
router.register(r'user-playlists', UserPlaylistViewSet, basename='user-playlist')
router.register(r'favorite-songs', UserFavoriteViewSet, basename='favorite-song')

urlpatterns = [
    path('api/', include(router.urls)),
    path('stream_song/<slug:song_id>/', stream_song, name='stream_song'),
    path('stream_video/<slug:song_id>/', stream_video, name='stream_video'),
    path('api/search/', SearchView.as_view(), name='search'),
    path('api/musicians/<int:pk>/follow/', MusicianViewSet.as_view({'post': 'follow'}), name='musician-follow'),
    path('api/musicians/<int:pk>/unfollow/', MusicianViewSet.as_view({'post': 'unfollow'}), name='musician-unfollow'),
    path('api/musicians/following/', MusicianViewSet.as_view({'get': 'following'}), name='musician-following'),
    path('api/user-playlists/<str:pk>/add-song/', 
         UserPlaylistViewSet.as_view({'post': 'add_song'}), 
         name='playlist-add-song'),
    path('api/user-playlists/<str:pk>/remove-song/', 
         UserPlaylistViewSet.as_view({'post': 'remove_song'}), 
         name='playlist-remove-song'),
]
    