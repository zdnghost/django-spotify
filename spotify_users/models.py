from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django_mongodb_backend.fields import ObjectIdAutoField
from spotify_app.models import Musician

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email không được để trống')
        if not username:
            raise ValueError('Username không được để trống')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('birthday', '1990/01/01')
        extra_fields.setdefault('gender', True)
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = ObjectIdAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    birthday = models.DateField()
    gender = models.BooleanField()  # True: Nam, False: Nữ
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_image = models.CharField(max_length=255, blank=True)

    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'spotify_users'
        managed = False
    
    def __str__(self):
        if self.email is None:
            return "User email is None"
        return self.email

class UserFollow(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_follows'
        managed = False
        unique_together = ('user', 'musician')
    
    def __str__(self):
        return f"{self.user.username} follows {self.musician.musician_name}"