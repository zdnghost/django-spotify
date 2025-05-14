from django.apps import AppConfig

class SpotifyUsersConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'spotify_users'