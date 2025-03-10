from rest_framework import viewsets
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Streak, Achievement


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete_quiz(self, request, pk=None):
        """ Mark a quiz as completed and update streak """
        quiz = self.get_object()

        if request.user in quiz.completed_by.all():
            return Response({"message": "Quiz already completed!"}, status=400)

        quiz.completed_by.add(request.user)  # Mark quiz as completed

        # Update streak
        streak, _ = Streak.objects.get_or_create(user=request.user)
        streak.current_streak += 1
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        streak.save()

        # Award Achievements
        completed_quizzes_count = request.user.completed_quizzes.count()
        if completed_quizzes_count == 5:
            Achievement.objects.get_or_create(
                user=request.user, 
                title="Quiz Master",
                description="Completed 5 quizzes!",
            )

        return Response({"message": "Quiz completed! Streak updated."})

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
