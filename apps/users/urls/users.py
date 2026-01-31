"""
User management URL patterns for Users app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet

app_name = "users"

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
