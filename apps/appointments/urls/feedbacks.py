"""
Feedbacks URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.appointments.views import FeedbackViewSet

app_name = "feedbacks"

router = DefaultRouter()
router.register("", FeedbackViewSet, basename="feedback")

urlpatterns = [
    path("", include(router.urls)),
]
