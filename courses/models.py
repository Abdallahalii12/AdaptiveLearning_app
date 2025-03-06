from django.db import models
from django.conf import settings
import cloudinary.models



class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    video = cloudinary.models.CloudinaryField('video', resource_type='video', blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)

    category = models.CharField(max_length=50, choices=[
        ("programming", "Programming"),
        ("design", "Design"),
        ("business", "Business"),
    ])
    duration = models.DurationField()  
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields
    students_enrolled = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Enrollment", related_name="enrolled_courses")
    status = models.CharField(max_length=20, choices=[("draft", "Draft"), ("published", "Published")], default="draft")
    requirements = models.TextField(blank=True, null=True)
    learning_outcomes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


# 📌 Enrollment Model (For tracking course enrollment)
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("completed", "Completed")])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment")
        ]


# 📌 Lesson Model
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    video = cloudinary.models.CloudinaryField('video', resource_type='video', blank=True, null=True)
    order = models.PositiveIntegerField(default=1)  # Order of the lesson in the course
    is_published = models.BooleanField(default=False)  # Draft or Published
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="completed_lessons", blank=True)  # Track completed students

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# 📌 Lesson Quiz Model
class LessonQuiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=20, choices=[
        ("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")
    ], default="medium")
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="completed_quizzes", blank=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


# 📌 Lesson Question Model
class LessonQuestion(models.Model):
    quiz = models.ForeignKey(LessonQuiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[('mcq', 'Multiple Choice'), ('text', 'Text Input')])
    correct_answer = models.CharField(max_length=255, blank=True, null=True)  # For text-based answers
    points = models.PositiveIntegerField(default=1)  # Score for this question

    def __str__(self):
        return self.text


# 📌 Lesson Answer Model
class LessonAnswer(models.Model):
    question = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, null=True)  # Explanation for the answer

    def __str__(self):
        return self.text


# 📌 Streaks & Achievement Tracking

# Streak Model
class Streak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateField(auto_now=True)  # Track the last day the user was active

    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak}"


# Achievement Model
class Achievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)  # If related to a course
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_earned = models.DateTimeField(auto_now_add=True)
    badge_image = models.ImageField(upload_to="achievement_badges/", blank=True, null=True)  # Badge image

    def __str__(self):
        return f"{self.user.username} - {self.title}"









