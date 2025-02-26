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
            role=validated_data.get('role')  # Add the role field
        )
        return user


class LoginSerializer(serializers.Serializer):  # Change to Serializer
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

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


