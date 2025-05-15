from rest_framework import serializers
from .models import CustomUser, UserFollow
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from spotify_app.models import Musician
from spotify_app.serializers import MusicianSerializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all(), message="Email này đã được sử dụng.")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all(), message="Username này đã được sử dụng.")]
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm', 'birthday', 'gender']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Mật khẩu không khớp."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                raise serializers.ValidationError('Email hoặc mật khẩu không chính xác.')
            if not user.is_active:
                raise serializers.ValidationError('Tài khoản này đã bị vô hiệu hóa.')
        else:
            raise serializers.ValidationError('Email và mật khẩu là bắt buộc.')
        
        data['user'] = user
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        
        token['user_id'] = str(user.id)
        token['email'] = user.email
        token['username'] = user.username
        
        return token

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    followed_musicians_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'date_joined', 'birthday', 
                  'gender', 'profile_image', 'followed_musicians_count']
        read_only_fields = ['id', 'email', 'date_joined', 'followed_musicians_count']
    
    def get_id(self, obj):
        return str(obj.id)
    
    def get_followed_musicians_count(self, obj):
        return UserFollow.objects.filter(user=obj).count()

class UserFollowSerializer(serializers.ModelSerializer):
    musician_details = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFollow
        fields = ['id', 'musician', 'followed_at', 'musician_details']
        read_only_fields = ['id', 'followed_at']
    
    def get_musician_details(self, obj):
        return {
            'id': str(obj.musician.id),
            'name': obj.musician.musician_name,
            'followers': obj.musician.number_of_follower
        }