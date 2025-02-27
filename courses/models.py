from django.db import models
from django.conf import settings

# Create your models here.
class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.ImageField(upload_to="course_images/")
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
         
     course = models.ForeignKey(Course, on_delete=models.CASCADE)
     title = models.CharField(max_length=200)  # Title of the lesson
     topic = models.TextField()  # Content or topic covered
     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for tracking

     def __str__(self):
         return self.title
     


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
       
        if self.lesson and self.course:
            raise ValidationError("A quiz must be linked to either a lesson or a course, not both.")
        if not self.lesson and not self.course:
            raise ValidationError("A quiz must be linked to at least a lesson or a course.")









