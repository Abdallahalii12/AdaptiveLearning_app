from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreadViewSet, PostViewSet, LikeViewSet, ReportViewSet

router = DefaultRouter()
router.register(r"threads", ThreadViewSet)
router.register(r"posts", PostViewSet)
router.register(r"likes", LikeViewSet)
router.register(r"reports", ReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
