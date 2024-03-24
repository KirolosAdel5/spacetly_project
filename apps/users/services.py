import requests
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from urllib.parse import urlencode
from rest_framework_simplejwt.tokens import RefreshToken
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from random import SystemRandom

class GoogleRawLoginFlowService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        # This is how it's implemented in the official SDK
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def get_authorization_url(self):
        redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
        scopes = "email profile"
        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scopes,
            "state": state,
            
        }
        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"
    
        return authorization_url, state

    def get_access_token(self, code, redirect_uri):
        params = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(self.GOOGLE_TOKEN_URL, data=params)
        return response.json()

    def get_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.GOOGLE_USERINFO_URL, headers=headers)
        return response.json()

    def get_access_and_refresh_tokens(self, user):
        serializer = TokenObtainPairSerializer()
        token_data = serializer.get_token(user)
        access_token = token_data.access_token
        refresh_token = RefreshToken.for_user(user)
        return access_token, refresh_token
    
    
class FacebookRawLoginFlowService:
    def __init__(self):
        self.client_id = settings.FACEBOOK_APP_ID
        self.client_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
        self.state = 'your_custom_state'  # Replace with your state logic

    def get_authorization_url(self):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'email'  # Add any additional scopes as needed
        }
        authorization_url = 'https://www.facebook.com/v12.0/dialog/oauth?' + urlencode(params)
        return authorization_url
    def get_access_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        response = requests.get('https://graph.facebook.com/v12.0/oauth/access_token', params=params)
        return response.json()

    def get_user_info(self, access_token):
        params = {
            'access_token': access_token,
            'fields': 'id,name,email'  # Customize fields as needed
        }
        user_info_url = 'https://graph.facebook.com/v12.0/me'
        response = requests.get(user_info_url, params=params)
        data = response.json()
        return data
    
    def get_access_and_refresh_tokens(self, user):
        serializer = TokenObtainPairSerializer()
        token_data = serializer.get_token(user)
        access_token = token_data.access_token
        refresh_token = RefreshToken.for_user(user)
        return access_token, refresh_token