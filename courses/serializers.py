from rest_framework import serializers
from .models import Course, Enrollment, Lesson,LessonQuiz,LessonQuestion,LessonAnswer

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAnswer
        fields = ['id', 'question', 'text', 'is_correct']

class LessonQuestionSerializer(serializers.ModelSerializer):
    answers = LessonAnswerSerializer(many=True, read_only=True)  # Nested answers

    class Meta:
        model = LessonQuestion
        fields = ['id', 'quiz', 'text', 'question_type', 'answers']

class LessonQuizSerializer(serializers.ModelSerializer):
    questions = LessonQuestionSerializer(many=True, read_only=True)  # Nested questions

    class Meta:
        model = LessonQuiz
        fields = ['id', 'lesson', 'title', 'questions']