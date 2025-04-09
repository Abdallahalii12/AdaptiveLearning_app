from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Thread, Post, Like, Report
from .serializers import ThreadSerializer, PostSerializer, LikeSerializer, ReportSerializer
from .permissions import IsOwnerOrReadOnly
from courses.models import Course


# ViewSet for managing Threads
class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'author', 'is_pinned', 'is_closed']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'reply_count', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'student':
                return Thread.objects.filter(
                    course__enrollments__student=user,
                    course__status='published'
                )
            elif user.role == 'instructor':
                return Thread.objects.filter(
                    course__instructor=user
                )
        return Thread.objects.filter(course__status='published')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pin(self, request, pk=None):
        thread = self.get_object()
        if request.user != thread.course.instructor:
            return Response(
                {"error": "Only course instructors can pin threads."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        thread.is_pinned = not thread.is_pinned
        thread.save()
        return Response({"message": f"Thread {'pinned' if thread.is_pinned else 'unpinned'} successfully."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def close(self, request, pk=None):
        thread = self.get_object()
        if request.user != thread.course.instructor and request.user != thread.author:
            return Response(
                {"error": "Only course instructors or thread authors can close threads."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        thread.is_closed = not thread.is_closed
        thread.save()
        return Response({"message": f"Thread {'closed' if thread.is_closed else 'reopened'} successfully."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_post(self, request, pk=None):
        thread = self.get_object()
        if thread.is_closed:
            return Response(
                {"error": "Cannot post in closed threads."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if thread.course.status != 'published':
            return Response(
                {"error": "Cannot post in threads of unpublished courses."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.role == 'student':
            enrollment = thread.course.enrollments.filter(
                student=request.user,
                status='active'
            ).first()
            if not enrollment:
                return Response(
                    {"error": "You must be enrolled in the course to post."},
                    status=status.HTTP_403_FORBIDDEN
                )

        data = request.data.copy()
        data['thread'] = thread.pk
        serializer = PostSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            thread.reply_count = thread.posts.count()
            thread.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ViewSet for managing Posts
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['thread', 'author', 'parent', 'is_edited']
    search_fields = ['content']
    ordering_fields = ['created_at', 'like_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'student':
                return Post.objects.filter(
                    thread__course__enrollments__student=user,
                    thread__course__status='published'
                )
            elif user.role == 'instructor':
                return Post.objects.filter(
                    thread__course__instructor=user
                )
        return Post.objects.filter(thread__course__status='published')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def edit(self, request, pk=None):
        post = self.get_object()
        if request.user != post.author:
            return Response(
                {"error": "You can only edit your own posts."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            post = serializer.save(is_edited=True)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            post.like_count = post.likes.count()
            post.save()
            return Response({"message": "Post unliked."})
        
        post.like_count = post.likes.count()
        post.save()
        return Response({"message": "Post liked."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        post = self.get_object()
        reason = request.data.get('reason')
        
        if not reason:
            return Response(
                {"error": "Reason is required for reporting."},
                status=status.HTTP_400_BAD_REQUEST
            )

        report = Report.objects.create(
            post=post,
            user=request.user,
            reason=reason
        )
        
        return Response(
            {"message": "Post reported successfully."},
            status=status.HTTP_201_CREATED
        )


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
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['post', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'instructor':
            return Report.objects.filter(
                post__thread__course__instructor=user
            )
        return Report.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
