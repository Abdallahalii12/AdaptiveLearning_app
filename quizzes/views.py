from django.shortcuts import render
from courses import permissons

# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        """Set permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:  
            return [IsAuthenticated(), IsInstructor()]  # Only instructors can modify quizzes
        return [IsAuthenticated()]  # Any logged-in user can view or attempt quizzes
