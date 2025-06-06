from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserFollowSerializer
from .models import CustomUser, UserFollow
from rest_framework.decorators import api_view, permission_classes
from spotify_app.models import Musician
from spotify_app.serializers import MusicianSerializer

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': tokens,
                'message': 'Đăng ký tài khoản thành công!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': tokens,
                'message': 'Đăng nhập thành công!'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data': serializer.data,
                'message': 'Cập nhật thông tin thành công!'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFollowedMusiciansView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):

        user = request.user
        follows = UserFollow.objects.filter(user=user).select_related('musician')
        

        musician_ids = [follow.musician.id for follow in follows]
        musicians = Musician.objects.filter(id__in=musician_ids)
        
        serializer = MusicianSerializer(musicians, many=True, context={'request': request})
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            return Response({'message': 'Đăng xuất thành công!'}, status=status.HTTP_200_OK)
        return Response({'error': 'Refresh token là cần thiết'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)