from django.db import models
from users.models import CustomUser

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.user.email
