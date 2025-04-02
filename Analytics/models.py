from django.db import models
from django.conf import settings
from courses.models import LessonQuiz,Lesson,Course
from quizzes.models import Quiz

# Create your models here.
class UserActivityLog(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="activity_logs")
    lesson_quiz=models.ForeignKey(LessonQuiz,on_delete=models.CASCADE,related_name="lesson_quiz_attempts",blank=True,null=True)
    big_quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,related_name="big_quiz_attempts",blank=True,null=True)
    lessons_watched=models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name="lessons_watched",null=True,blank=True)
    time_stamp=models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.time_stamp}"


class InstructorAnalytics(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="instructor_insights")
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="course_insights")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_insights")

    total_students = models.PositiveIntegerField(default=0)  
    average_quiz_score = models.FloatField(null=True, blank=True)  
    completion_rate = models.FloatField(null=True, blank=True)  
    drop_off_rate = models.FloatField(null=True, blank=True)  

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.course.title} by {self.user.username}"

    


class AdminReport(models.Model):
    pass

