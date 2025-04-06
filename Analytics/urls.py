from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserActivityViewSet,InstructorAnalyticsViewSet,StudentAnalyticsAPIView

router=DefaultRouter()
router.register(r'',UserActivityViewSet)
router.register(r'',InstructorAnalyticsViewSet)
router.register(r'',StudentAnalyticsAPIView)
urlpatterns=[
    path('',include(router.urls)),
]