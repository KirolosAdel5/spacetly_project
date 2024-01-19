from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.decorators import action
from django.contrib.auth import get_user_model,authenticate
from .serializers import SingUpSerializer,UserSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import random
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes,parser_classes
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from .permissions import IsAdminOrPostOnly 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.parsers import MultiPartParser, FormParser


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = [IsAdminOrPostOnly]
    lookup_field = 'username'


    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate a 4-digit OTP and store it in the user's profile
            otp = random.randint(1000, 9999)
            user.otp = otp
            user.otp_created_at = timezone.now()

            user.save()

            # Send the OTP to the user via email
            current_site = 'Spacetly.com'
            subject = 'Your verification OTP on {0}'.format(current_site)
            message = f'Your verification OTP is: {otp}'
            user.email_user(subject, message)

            refresh = RefreshToken.for_user(user)
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response({'user': serializer.data, 'tokens': token_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm_email(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(pk=str(user_id))
            if user.email_verified:
                return Response({'detail': 'Email already confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.otp == int(otp) and self.is_otp_valid(user.otp_created_at):
                user.email_verified = True
                user.save()
                return Response({'detail': 'Email confirmed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Unable to verify your email address.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'detail': 'Invalid user ID.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def is_otp_valid(self, otp_created_at):
        # Check if the OTP is still valid based on the expiration time
        if otp_created_at:
            expiration_time = otp_created_at + timezone.timedelta(minutes=5)
            return timezone.now() <= expiration_time
        return False
    
    @action(detail=False, methods=['post'])
    def send_reset_otp(self, request):
        email = request.data.get('email', '')
        print(email)
        try:
            user = User.objects.get(email=email)

            # Generate a new 4-digit OTP and update it in the user's profile
            otp = random.randint(1000, 9999)
            user.otp = otp
            user.save()

            # Send the new OTP to the user via email
            current_site = 'Spacetly.com'
            subject = 'Your reset OTP on {0}'.format(current_site)
            message = f'Your reset OTP is: {otp}'
            user.email_user(subject, message)

            return Response({'detail': 'Reset OTP sent successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # @action(detail=False, methods=['post'], url_path='login')
    # def login(self, request):
    #     email = request.data.get('email')
    #     password = request.data.get('password')
    #     user = User.objects.get(email=email)

    #     if user is not None:
    #         refresh = RefreshToken.for_user(user)
    #         token_data = {
    #             'refresh': str(refresh),
    #             'access': str(refresh.access_token),
    #         }

    #         # Add the refresh token to the outstanding tokens
    #         user.outstanding_tokens.append(str(refresh))
    #         user.save()

    #         django_login(request, user)

    #         return Response({'user': SingUpSerializer(user).data, 'tokens': token_data}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user, many=False)
    return Response(user.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_user(request):
    user = request.user
    data = request.data

    user.name = data.get('name', user.name)
    user.username = data.get('username', user.username)

    if 'password' in data and data['password'] != "":
        user.password = make_password(data['password'])

    # Check if 'profile_picture' is present in the request data
    if 'profile_picture' in request.data:
        user.profile_picture = request.data['profile_picture']

    user.save()
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)


@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User,email=data['email'])
    token = get_random_string(40)
    expire_date = datetime.now() + timedelta(minutes=10)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_date
    user.profile.save()
    
    host = get_current_host(request)
    link = "http://localhost:8000/api/reset_password/{token}".format(token=token)
    body = "Your password reset link is : {link}".format(link=link)
    send_mail(
        "Paswword reset from Spacetly",
        body,
        "Spacetly@gmail.com",
        [data['email']]
    )
    return Response({'details': 'Password reset sent to {email}'.format(email=data['email'])})

 
@api_view(['POST'])
def reset_password(request,token):
    data = request.data
    try:
        user = User.objects.get(profile__reset_password_token=token)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST
        )
    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'error': 'Password are not same'},status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None 
    user.profile.save() 
    user.save()
    return Response({'details': 'Password reset done '})

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.get(email=email)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            django_login(request, user)

            return Response({'user': UserSerializer(user).data, 'tokens': data}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class APILogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if self.request.data.get('all'):
            token: OutstandingToken
            for token in OutstandingToken.objects.filter(user=request.user):
                _, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
        refresh_token = self.request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        logout(request)
        return Response({"status": "OK, goodbye"})
    
    
            
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_user_permissions(request, username):
    # Check if the requesting user is a superuser or staff
    if not (request.user.is_superuser or request.user.is_staff):
        return Response({"error": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    is_staff = data.get('is_staff', False)
    is_superuser = data.get('is_superuser', False)

    # Only superusers can set superuser flag
    if request.user.is_superuser:
        user.is_superuser = is_superuser

    # Both superusers and staff can set staff flag
    user.is_staff = is_staff

    user.save()

    return Response({"message": "User permissions updated successfully"}, status=status.HTTP_200_OK)
