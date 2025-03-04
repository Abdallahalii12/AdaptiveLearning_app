from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='course_videos/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="course_images/")
    image = models.URLField()
    category = models.CharField(max_length=50, choices=[
        ("programming", "Programming"),
        ("design", "Design"),
        ("business", "Business"),
    ])
    duration = models.DurationField() 
    created_at = models.DateTimeField(auto_now_add=True)  




class Enrollment(models.Model):
    user =models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    course =models.ForeignKey(Course,on_delete=models.CASCADE)
    enrolled_at=models.DateTimeField(auto_now_add=True)
    progress=models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("completed", "Completed")])


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment")

        ]
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    video = models.FileField(upload_to='lesson_videos/', blank=True, null=True)

class LessonQuiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)

class LessonQuestion(models.Model):
    quiz = models.ForeignKey(LessonQuiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[('mcq', 'Multiple Choice'), ('text', 'Text Input')])

class LessonAnswer(models.Model):
    question = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

     










