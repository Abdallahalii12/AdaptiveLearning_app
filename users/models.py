from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, RegexValidator

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        error_messages={
            'unique': 'A user with that email already exists.',
        }
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )
    is_banned = models.BooleanField(default=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer.',
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers and underscores.'
            )
        ]
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email
