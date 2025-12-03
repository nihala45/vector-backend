from django.urls import path, include
from .views import UserRegisterView, VerifyOTPView, UserLoginView, UserLogoutView, ResendOtp, ForgetPassword
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


urlpatterns = [
    path('register/',UserRegisterView.as_view(), name='user_register'),
    path('verify_otp/<int:pk>/',VerifyOTPView.as_view(), name='verify_otp'),
    path('resend_otp/<int:pk>/', ResendOtp.as_view(), name='resend_otp'),
    path('forget_password/', ForgetPassword.as_view(), name='forget_password'),
    
    
    path('login/',UserLoginView.as_view(), name='user-login'),
    path('logout/',UserLogoutView.as_view(), name='user-logout'), 
    path('', include(router.urls)),
]