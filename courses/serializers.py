from rest_framework import serializers
from .models import Course, Enrollment, Lesson, LessonQuiz, LessonQuestion, LessonAnswer, Streak, Achievement

# 📌 Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    students_enrolled = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Show enrolled students
    
    class Meta:
        model = Course
        fields = ['id', 'instructor', 'title', 'video', 'description', 'price', 'image', 'category', 
                  'duration', 'created_at', 'status', 'requirements', 'learning_outcomes', 'students_enrolled']

# 📌 Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

# 📌 Lesson Serializer
class LessonSerializer(serializers.ModelSerializer):
    completed_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Track who completed it
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'content', 'video', 'order', 'is_published', 'completed_by']

# 📌 Lesson Answer Serializer
class LessonAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAnswer
        fields = ['id', 'question', 'text', 'is_correct', 'explanation']

# 📌 Lesson Question Serializer (Includes Answers)
class LessonQuestionSerializer(serializers.ModelSerializer):
    answers = LessonAnswerSerializer(many=True, read_only=True)  # Nested answers

    class Meta:
        model = LessonQuestion
        fields = ['id', 'quiz', 'text', 'question_type', 'correct_answer', 'points', 'answers']

# 📌 Lesson Quiz Serializer (Includes Questions & Completed Users)
class LessonQuizSerializer(serializers.ModelSerializer):
    questions = LessonQuestionSerializer(many=True, read_only=True)  # Nested questions
    completed_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Track who completed it

    class Meta:
        model = LessonQuiz
        fields = ['id', 'lesson', 'title', 'difficulty', 'questions', 'completed_by']

# 📌 Streak Serializer
class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ['user', 'current_streak', 'longest_streak', 'last_activity']

# 📌 Achievement Serializer
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'user', 'course', 'title', 'description', 'date_earned', 'badge_image']
