from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserActivityViewSet,InstructorAnalyticsViewSet

router=DefaultRouter()
router.register(r'',UserActivityViewSet)
router.register(r'',InstructorAnalyticsViewSet)
urlpatterns=[
    path('',include(router.urls)),
]