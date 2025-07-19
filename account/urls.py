from django.urls import path, include
from .views import RegisterView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


urlpatterns = [
    path('user/register/',RegisterView.as_view(), name='user_register'),
]