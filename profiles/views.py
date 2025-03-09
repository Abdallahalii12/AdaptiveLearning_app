from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

    def get_queryset(self):
        """
        Returns only the profile of the logged-in user.
        """
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Ensures that a user can only update their own profile.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['patch', 'put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Custom method to allow a user to update their profile.
        """
        user_profile = self.get_queryset().first()  # Retrieve the user's profile
        if not user_profile:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
