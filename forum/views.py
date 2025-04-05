from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Thread, Post, Like, Report
from .serializers import ThreadSerializer, PostSerializer, LikeSerializer, ReportSerializer
from .permissions import IsOwnerOrReadOnly


# ViewSet for managing Threads
class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all().order_by('-created_at')  # Get all threads, ordered by creation date
    serializer_class = ThreadSerializer  # Specify the serializer to use
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]  # Define permissions

    # Custom action to add a Post to a Thread
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_post(self, request, pk=None):
        thread = self.get_object()  # Get the thread based on the pk (primary key)
        data = request.data.copy()  # Copy the request data
        
        # Manually add the thread to the data
        data['thread'] = thread.pk

        # Initialize the PostSerializer to validate the data
        serializer = PostSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)  # Save the post with the current user as the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the created post
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if validation fails


# ViewSet for managing Posts
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')  # Get all posts, ordered by creation date
    serializer_class = PostSerializer  # Specify the serializer to use
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]  # Define permissions

    def perform_create(self, serializer):
        # Save the post with the current user as the author
        serializer.save(author=self.request.user)


# ViewSet for managing Likes
class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()  # Get all likes
    serializer_class = LikeSerializer  # Specify the serializer to use
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can like posts

    def perform_create(self, serializer):
        # Save the like with the current user
        serializer.save(user=self.request.user)


# ViewSet for managing Reports
class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()  # Get all reports
    serializer_class = ReportSerializer  # Specify the serializer to use
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can report content

    def perform_create(self, serializer):
        # Save the report with the current user
        serializer.save(user=self.request.user)
