from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .utils import custom_response




# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return custom_response(success=True, message="User registered successfully", status=status.HTTP_201_CREATED)
        return custom_response(success=False, message="Registration failed", data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    


    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return custom_response(success=False, message="Invalid credentials", data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        if user.is_active:
            refresh = RefreshToken.for_user(user)
            return custom_response(
                success=True,
                message="Login successful",
                data={
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "access_token_expiry": refresh.access_token.payload['exp'],
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "role": user.role
                    }
                },
                status=status.HTTP_200_OK
            )
        return custom_response(success=False, message="User is inactive", status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            return custom_response(success=True, message="Logout successful", status=status.HTTP_200_OK)
        return custom_response(success=False, message="Invalid request", data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)