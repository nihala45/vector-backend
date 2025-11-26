from django.urls import path, include
from .views import UserRegisterView, VerifyOTPView, UserLoginView, UserLogoutView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


urlpatterns = [
    path('register/',UserRegisterView.as_view(), name='user_register'),
 path('verify_otp/<int:pk>/',VerifyOTPView.as_view(), name='verify_otp'),
    path('login/',UserLoginView.as_view(), name='user-login'),
    path('logout/',UserLogoutView.as_view(), name='user-logout'), 
    path('', include(router.urls)),
]