from rest_framework import viewsets
from .models import Quiz, Question, Answer,QuizSubmission
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Streak, Achievement
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


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

class QuizSubmission(APIView):
    permission_classes=[IsAuthenticated]

    def Post(self,request,quiz_id):
        quiz = get_object_404(Quiz,id=quiz_id)
        user =request.user

        if QuizSubmission.objects.filter(quiz=quiz,user=user).exists():
            return Response({"error:you have already submitted this quiz"},status=400)
        
        submitted_answer=request.data("answers",{})
        questions=quiz.questions.all()
        correct_count=0
        # Check if MCQ or text input
        if question.question_type == "mcq":
                correct_option = question.answers.filter(is_correct=True).first()
                if correct_option and user_answer == str(correct_option.id):
                    correct_count += 1
                else:
               
                 if user_answer and user_answer.strip().lower() == correct_answer.strip().lower():
                    correct_count += 1

        # Calculate score
        total_questions = questions.count()
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        # Save submission
        QuizSubmission.objects.create(quiz=quiz, user=user, score=score)

        return Response({"message": "Quiz submitted successfully!", "score": score})

     