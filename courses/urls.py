from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet, LessonViewSet,LessonQuizViewSet

router = DefaultRouter()
router.register(r'', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'lessons-quizzes',LessonQuizViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
