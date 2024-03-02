from ..users.models import User
from rest_framework import serializers
from django.db import IntegrityError
from rest_framework.response import Response
import re
from django.contrib.auth.password_validation import validate_password
import random



class AdminUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    date_joined_date = serializers.SerializerMethodField()
    date_joined_time = serializers.SerializerMethodField()
    words_left = serializers.SerializerMethodField(read_only=True)
    images_left = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'email_verified', 'profile_picture', 'subscription_plan','is_staff','is_active','date_joined_date', 'date_joined_time','words_left', 'images_left', 'country']
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'required': True},
                        'username': {'read_only': True}
                        }
        
    
    def get_words_left(self, instance):
        return random.randint(0, 2500)

    def get_images_left(self, instance):
        return random.randint(0, 15)

    def get_country(self, instance):
        countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany']  # Add more countries as needed
        return random.choice(countries)
    def get_date_joined_date(self, instance):
        # Format the date_joined field to return only the date
        return instance.date_joined.strftime("%d %b %Y")

    def get_date_joined_time(self, instance):
        # Format the date_joined field to return only the time
        return instance.date_joined.strftime("%I:%M %p")

    def validate_email(self, value):
        # Check if email is already registered
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")

        return value

    def validate_password(self, value):
        # Check for strong password
        if not re.search(r'\d', value) or not re.search('[A-Z]', value):
            raise serializers.ValidationError("Password should contain at least 1 number and 1 uppercase letter.")

        validate_password(value)
        return value

    def create(self, validated_data):
        name = validated_data['name']
        email = validated_data['email']
        password = validated_data['password']

        # Generate a unique username if the provided name already exists as a username
       
        base_username = re.sub(r'\s+', '_', name).lower()

        while True:
            random_number = random.randint(1000, 9999)
            unique_username = f"{base_username}_{random_number}"
            try:
                User.objects.get(username=unique_username)
            except User.DoesNotExist:
                name = unique_username
                break

        user = User.objects.create_user(
            name,
            email,
            password
        )
        user.name = validated_data['name']
        user.save()
        
        return user
