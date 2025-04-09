from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreadViewSet, PostViewSet, LikeViewSet, ReportViewSet

router = DefaultRouter()
router.register(r"threads", ThreadViewSet, basename='thread')
router.register(r"posts", PostViewSet, basename='post')
router.register(r"likes", LikeViewSet, basename='like')
router.register(r"reports", ReportViewSet, basename='report')

urlpatterns = [
    path("", include(router.urls)),
]
