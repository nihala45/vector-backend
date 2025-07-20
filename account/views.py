from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken  
from .models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .signal import generate_otp, send_otp_email

from .api.user_serializers import (
    UserSerializers, 
    CustomTokenObtainPairSerializer, 
    UserStatusSerializer, 
    ChangePasswordSerializer
)

class RegisterView(APIView):
    """
    Handles user registration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        
        user_serializer = UserSerializers(data=data)

        # Validate and save user data
        if user_serializer.is_valid():
            try:
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerification(APIView):
    """
    Handles OTP verification for user registration or password reset.
    """
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        # Check if the user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data='User not found')
        
        # Check OTP expiration and validity
        if not user.otp:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='OTP is Expired')

        if user.otp == otp:
            user.otp = None
            user.is_verified = True
            user.save()
            return Response(data='OTP verifed successfully', status=status.HTTP_200_OK)
        return Response(data='Invalid OTP', status=status.HTTP_400_BAD_REQUEST)
        

class ResendOtpView(APIView):
    """
    Resends OTP for verification.
    """
    def post(self,request):
        email = request.data.get('email')

        if not email:
            return Response(data='Email is required', status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data="User not Found", status=status.HTTP_404_NOT_FOUND)
        
       # Generate and send new OTP
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_otp_email(email, otp)

        return Response(data='OTP resent successfully', status=status.HTTP_200_OK)

    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Token Obtain Pair View using a custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ForgetPassword(APIView):
    """
    Handles the password reset process including OTP generation.
    """
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if not email:
            return Response(data={'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data={'error': 'User account not found'}, status=status.HTTP_404_NOT_FOUND)

        # If password is provided, change it directly
        if password:
            user.set_password(password)
            user.save()
            return Response(data={'message': 'Password changed successfully'}, status=status.HTTP_201_CREATED)

        # If password is not provided, generate OTP for password reset
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_otp_email(email, otp)

        return Response(data={'message': 'OTP sent for password reset', 'role': user.role}, status=status.HTTP_200_OK)
       

class Logout(APIView):
    """
    Handles user logout and token blacklist.
    """
    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)