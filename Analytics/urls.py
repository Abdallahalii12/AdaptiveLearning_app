from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserActivityLogViewSet, InstructorAnalyticsViewSet, StudentAnalyticsAPIView

router = DefaultRouter()
router.register(r'user-activity', UserActivityLogViewSet, basename='user-activity')
router.register(r'instructor-analytics', InstructorAnalyticsViewSet, basename='instructor-analytics')

urlpatterns = [
    path('', include(router.urls)),
    path('student-analytics/', StudentAnalyticsAPIView.as_view(), name='student-analytics'),
]
