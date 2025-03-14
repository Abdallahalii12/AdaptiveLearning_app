from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'role'] 

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role')  
        )
        return user


class LoginSerializer(serializers.Serializer):##
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        if not isinstance(user, CustomUser):  
            raise serializers.ValidationError("Authentication failed.")

        if user.is_banned:
            raise serializers.ValidationError("Your account has been banned. Contact support.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive. Contact support.")

        # Add user to validated_data so that LoginView can access it
        data["user"] = user
        return data
        
class LogoutSerializer(serializers.Serializer):
        refresh = serializers.CharField()

        def validate(self,data):
            try:
                token = RefreshToken(data["refresh"])  
                token.blacklist()  # Blacklist the token
            except TokenError:
                raise serializers.ValidationError("Invalid or expired refresh token.")

            return data


