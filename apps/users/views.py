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
from django.shortcuts import get_object_or_404, render,HttpResponse
from django.views.generic import View

from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from .permissions import IsAdminOrPostOnly 
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import redirect
from social_django.utils import load_strategy

from .services import GoogleRawLoginFlowService,FacebookRawLoginFlowService

import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
import re
from django.core.exceptions import ImproperlyConfigured
from attrs import define

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = [IsAdminOrPostOnly]

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
        else:
            email_errors = serializer.errors.get('email', [])
            password_errors = serializer.errors.get('password', [])

            if email_errors:
                return Response({'message': email_errors[0]}, status=status.HTTP_400_BAD_REQUEST)
            elif password_errors:
                return Response({'message': password_errors[0]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm_email(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(pk=str(user_id))
            if user.email_verified:
                return Response({'message': 'تم تاكيد البريد الالكتروني من قبل'}, status=status.HTTP_400_BAD_REQUEST)

            if user.otp == int(otp) and self.is_otp_valid(user.otp_created_at):
                user.email_verified = True
                user.save()
                return Response({'message': 'تم تاكيد البريد الالكتروني بنجاح'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'الكود الذي ادخلته غير صالح'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        
    def is_otp_valid(self, otp_created_at):
        # Check if the OTP is still valid based on the expiration time
        if otp_created_at:
            return otp_created_at <=  otp_created_at + timedelta(hours=2)
        return False

    
    @action(detail=False, methods=['post'])
    def send_reset_otp(self, request):
        email = request.data.get('email', '')
        if not email:  # Check if email is not provided in the request body
            return Response({'message': 'الايميل مطلوب.'}, status=status.HTTP_400_BAD_REQUEST)

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

            return Response({'message': 'تم ارسال الكود الجديد بنجاح'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)

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
    if 'profile_picture' in request.data:
        user.profile_picture = request.data['profile_picture']
        if user.profile_picture:
            user.profile_picture = request.data['profile_picture']
        else:
            # Set default profile picture if 'profile_picture' is not provided or empty
            user.profile_picture = 'default.jpg'


    if 'old_password' in data or 'password' in data:
        PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        if 'old_password' in data and 'new_password' in data and 'confirm_password' in data:
            old_password = data['old_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']

            # Check if the new password and confirm password are not empty
            if new_password and confirm_password:
                # Verify that the old password matches the user's current password
                if user.check_password(old_password):
                    # Check if the new password is the same as the old password
                    if new_password != old_password:
                        # Check if the new password and confirm password match
                        if new_password == confirm_password:
                            # Check if the new password meets the strength requirements
                            if re.match(PASSWORD_PATTERN, new_password):
                                # Set the new password
                                user.set_password(new_password)
                                # Save the user object
                                user.save()
                            else:
                                # Return an error response indicating that the password does not meet the strength requirements
                                return Response({"message": "يجب ان كلمة المرور تحتوي على حروف كبيرة وصغيرة ورقم ورمز واحد على الاقل"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            # Return an error response indicating that the new password and confirm password do not match
                            return Response({"message": "كلمة المرور غير متطابقة"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Return an error response indicating that the new password is the same as the old password
                        return Response({"message": "كلمة المرور الجديدة يجب ان تكون مختلفة"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Return an error response indicating that the old password is incorrect
                    return Response({"message": "كلمة المرور القديمة غير صحيح"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Return an error response indicating that the new password or confirm password is empty
                return Response({"message": "يرجى تعبئة كلمة المرور الجديدة وتأكيد كلمة المرور"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Return an error response indicating that the required fields are missing
            return Response({"message": "Old password, new password, and confirm password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if 'phone_number' in data:
        user.phone_number = data['phone_number']

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
    
    # host = get_current_host(request)
    link = "https://auth.mutqinai.com/#/newpassword/{token}".format(token=token)
    body = "Your password reset link is : {link}".format(link=link)
    send_mail(
        "Paswword reset from  mutqinai.com",
        body,
        "info@mutqinai.com",
        [data['email']]
    )
    return Response({'details': 'Password reset sent to {email}'.format(email=data['email']),'link': link,'token': token,})

 
@api_view(['POST'])
def reset_password(request,token):
    data = request.data
    try:
        user = User.objects.get(profile__reset_password_token=token)
    except User.DoesNotExist:
        return Response(
            {'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST
        )
    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'message': 'الرابط منتهي'},status=status.HTTP_400_BAD_REQUEST)
    
    if data['password'] != data['confirmPassword']:
        return Response({'message': 'كلمة المرور غير متطابقة'},status=status.HTTP_400_BAD_REQUEST)
    
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None 
    user.profile.save() 
    user.save()
    return Response({'message': 'تم تغيير كلمة المرور بنجاح'})

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            if not user.is_active:
                return Response({'message': 'تم تعطيل حسابك'}, status=status.HTTP_403_FORBIDDEN)

            if not user.email_verified:
                return Response({'user_id': user.id,'message': 'يرجي تفعيل البريد الالكتروني'}, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return Response({'user': UserSerializer(user).data, 'tokens': data}, status=status.HTTP_200_OK)
        #check if email not exist
        elif user is None:
            return Response({'message': 'لم يتم العثور على البريد الالكتروني'}, status=status.HTTP_401_UNAUTHORIZED)
            
        else:
            return Response({'message': 'خطاء في البريد الالكتروني او كلمة المرور'}, status=status.HTTP_401_UNAUTHORIZED)

@define
class GoogleRawLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str

def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleRawLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id
    )

    return credentials
   

class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()
    
class GoogleLoginRedirectView(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)

class GoogleLoginCallbackView(PublicApi):
        
    def get(self, request, *args, **kwargs):
        service = GoogleRawLoginFlowService()
        code = request.GET.get("code")
        state = request.GET.get("state")
        session_state = request.session.get("google_oauth2_state")
        
        if code is None or state is None:
            return Response(
                {"message": "Code and state are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if state != session_state:
            return Response(
                {"message": "Invalid state parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        
        redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
        credentials = service.get_access_token(code, redirect_uri)
        
        if "access_token" not in credentials:
            return Response(
                {"message": "Access token not found in response."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        access_token = credentials["access_token"]
        user_info = service.get_user_info(access_token)

        email = user_info.get("email")
        if not email:
            return Response(
                {"message": "الايميل غير موجود"},
                status=status.HTTP_400_BAD_REQUEST
            )
        #if not found user crete new user
        users_with_email = User.objects.filter(email=email)
        
        if not users_with_email.exists():   
            profile_picture_url = user_info.get("picture")
            if profile_picture_url:
                response = requests.get(profile_picture_url)
                if response.status_code == 200:
                    #upload image from gogle 
                    profile_picture = SimpleUploadedFile(
                        name="profile_picture.jpg",
                        content=response.content,
                        content_type="image/jpeg"
                    )
                    user = User.objects.create(
                        email=user_info.get("email"),
                        username=user_info.get("email"),
                        first_name=user_info.get("given_name"),
                        last_name=user_info.get("family_name", ""),
                        email_verified=True,
                        profile_picture=profile_picture
                    )
                    access_token, refresh_token = service.get_access_and_refresh_tokens(user)
                    response_data = {
                        "message": "User created successfully.",
                        "access_token": str(access_token),
                        "refresh_token": str(refresh_token),
                    }
            
            else:
                user = User.objects.create(
                    email=user_info.get("email"),
                    username=user_info.get("email"),
                    first_name=user_info.get("given_name"),
                    last_name=user_info.get("family_name", ""),
                    email_verified=True
                )
                access_token, refresh_token = service.get_access_and_refresh_tokens(user)
                response_data = {
                    "message": "User created successfully.",
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token),
                }

                    

        user = users_with_email.first()
        access_token, refresh_token = service.get_access_and_refresh_tokens(user)
        response_data = {
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
        }
        
        user.last_login = datetime.now()
        user.save()
        
        front_page_url = 'http://auth.mutqinai.com/#/control'
        redirect_url = f"{front_page_url}?access_token={str(access_token)}&refresh_token={str(refresh_token)}"
        return redirect(redirect_url)

        # return Response(response_data, status=status.HTTP_200_OK)

class FacebookLoginRedirectView(PublicApi):
    def get(self, request, *args, **kwargs):
        facebook_login_flow = FacebookRawLoginFlowService()
        authorization_url = facebook_login_flow.get_authorization_url()
        request.session["facebook_oauth2_state"] = facebook_login_flow.state
        return redirect(authorization_url)

class FacebookLoginCallbackView(PublicApi):
    def get(self, request, *args, **kwargs):
        service = FacebookRawLoginFlowService()
        code = request.GET.get("code")
        state = request.GET.get("state")
        session_state = request.session.get("facebook_oauth2_state")
        
        if code is None or state is None:
            return Response(
                {"message": "Code and state are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if state != session_state:
            return Response(
                {"message": "Invalid state parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        redirect_uri = settings.FACEBOOK_OAUTH2_REDIRECT_URI
        credentials = service.get_access_token(code)
        
        if "access_token" not in credentials:
            return Response(
                {"message": "Access token not found in response."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        access_token = credentials["access_token"]
        user_info = service.get_user_info(access_token)

        email = user_info.get("email")
        if not email:
            return Response(
                {"message": "Email not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process user creation or login logic
        users_with_email = User.objects.filter(email=email)
        
        if not users_with_email.exists():   
            # User doesn't exist, create a new user
            user = User.objects.create(
                email=user_info.get("email"),
                username=user_info.get("email"),
                first_name=user_info.get("given_name"),
                last_name=user_info.get("family_name", ""),
                email_verified=True
            )
            # Additional processing if needed
            
            # Example response data:
            access_token, refresh_token = service.get_access_and_refresh_tokens(user)
            response_data = {
                "message": "User created successfully.",
                "access_token": str(access_token),
            }
        else:
            # User already exists, perform login logic
            user = users_with_email.first()
            access_token, refresh_token = service.get_access_and_refresh_tokens(user)
            response_data = {
                "access_token": str(access_token),
            }
        
        # Save last login time
        user.last_login = datetime.now()
        user.save()
        
        # Redirect or respond with data
        front_page_url = 'http://localhost:8000/control'
        redirect_url = f"{front_page_url}?access_token={str(access_token)}&refresh_token={str(refresh_token)}"
        return redirect(redirect_url)

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
        return Response({"message": "ليس لديك صلاحيات لتغيير صلاحيات المستخدم"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"message": "المستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)

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
