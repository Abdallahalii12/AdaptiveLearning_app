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


class LessonQuizSerializer(serializers.ModelSeriailzer):
    model = LessonQuiz
    fields='__all__'

