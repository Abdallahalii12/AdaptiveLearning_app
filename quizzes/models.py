from django.db import models
from django.conf import settings
from courses.models import Course
from django.utils.timezone import now  




class Quiz(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="quizzes",null=True,blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="completed_standalone_quizzes",  
        blank=True
    )

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[('mcq', 'Multiple Choice'), ('text', 'Text Input')])
   

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    

class QuizSubmission(models.Model):
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name="quizsubmission")
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    score=models.FloatField(default=0)
    submitted_at=models.DateTimeField(auto_now_add=True)


class UserAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(null=True, blank=True)  # For text-based answers
    is_correct = models.BooleanField(default=False)


