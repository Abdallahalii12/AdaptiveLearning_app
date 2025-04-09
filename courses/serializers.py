from rest_framework import serializers
from .models import Course, Enrollment, Lesson, LessonQuiz, LessonQuestion, LessonAnswer, Streak, Achievement

#Course Search Serializer
class CourseSearchSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.username')
    
    class Meta:
        model = Course
        fields = ['title', 'instructor_name', 'image'] 

# 📌 Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    instructor_email = serializers.CharField(source='instructor.email', read_only=True)
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'instructor', 'instructor_name', 'instructor_email',
            'title', 'video', 'description', 'price', 'image', 'category',
            'duration', 'created_at', 'updated_at', 'status', 'requirements',
            'learning_outcomes', 'students_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_students_count(self, obj):
        return obj.students_enrolled.count()

# 📌 Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'student_email',
            'course', 'course_title', 'enrolled_at', 'last_accessed',
            'progress', 'status', 'completion_date'
        ]
        read_only_fields = ['enrolled_at', 'last_accessed']

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
