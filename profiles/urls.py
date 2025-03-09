from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')  # ✅ تحديد `basename`

urlpatterns = [
    path('', include(router.urls)),
]
