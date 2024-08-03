from django.urls import path
from . import views
from .models import Profile

urlpatterns = [
    path("<int:pk>/",  views.ProfileDetail.as_view(), name="profile-detail")
]