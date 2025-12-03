from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
import pyotp
from .models import Users
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
import random
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAdminUser

from rest_framework.decorators import action
from django.db import DataError, IntegrityError




class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        username = request.data.get("username", "").strip()
        phone = request.data.get("phone", "").strip()
        password = request.data.get("password")

        # REQUIRED FIELD CHECK
        if not email or not username or not phone or not password:
            return Response(
                {"msg": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for verified email
        if Users.objects.filter(email=email, is_email_verified=True).exists():
            return Response(
                {"email": "This email is already verified and registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for verified phone\     
        if Users.objects.filter(phone=phone, is_email_verified=True).exists():
            return Response(
                {"phone": "This phone number is already taken."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # DELETE any unverified account with same email or phone
        Users.objects.filter(email=email, is_email_verified=False).delete()
        Users.objects.filter(phone=phone, is_email_verified=False).delete()

        # Generate OTP
        otp_secret = pyotp.random_base32()
        totp = pyotp.TOTP(otp_secret, interval=300)
        otp = totp.now()
        print("OTP:", otp)

        # Create NEW user always
        user = Users(
            email=email,
            username=username,
            phone=phone,
            email_otp=otp
        )
        user.set_password(password)
        user.save()

        # Send OTP Email
        try:
            send_mail(
                subject='Email Verification OTP',
                message=f'Hi {user.username},\n\nYour OTP is: {otp}\nIt is valid for 5 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {"msg": "Failed to send OTP email", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "msg": "Registration successful. OTP sent to your email.",
                "id": user.id
            },
            status=status.HTTP_201_CREATED
        )
   
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        otp = request.data.get('email_otp')

        if not otp:
            return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(id=pk)

            if user.email_otp == otp:
                user.is_email_verified = True
                user.email_otp = None
                user.save()

                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'OTP verified successfully!',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_superuser': user.is_superuser,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)

        if not user.is_email_verified:
            return Response({'error': 'Email is not verified. Please verify your email to continue.'}, status=403)


        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_superuser': user.is_superuser,
                'id': user.id,
                'email': user.email,
            })

        return Response({'error': 'Invalid credentials'}, status=400)
    
    

class UserLogoutView(APIView):
   
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Logout successful"},
            status=status.HTTP_205_RESET_CONTENT
        )
        
class ResendOtp(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            user = Users.objects.get(id=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_email_verified:
            return Response({"msg": "Email already verified."}, status=400)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        print(otp,'ooooooooooooooooooooooooooooooooooo')
        user.email_otp = otp
        user.save(update_fields=["email_otp"])

        # Send email
        try:
            send_mail(
                subject="Your Verification OTP",
                message=f"Your OTP is: {otp}\nValid for 5 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except:
            return Response({"error": "Failed to send OTP"}, status=500)

        return Response({"msg": "OTP resent successfully"}, status=200)
    


class ForgetPassword(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"email": "Email is required"}, status=400)

        # Fetch user
        user = Users.objects.filter(email=email).first()

        if not user:
            return Response({"email": "No account found with this email"}, status=404)

        if not user.is_email_verified:
            return Response({"email": "Email is not verified. Please verify first."}, status=400)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        print("Reset Password OTP:", otp)

        # Save OTP
        user.email_otp = otp
        user.save(update_fields=["email_otp"])
       

        # Send email
        try:
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is: {otp}\nIt is valid for 5 minutes.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email error:", e)
            return Response({"error": "Failed to send OTP"}, status=500)

        return Response({
            "msg": "OTP sent successfully",
            "id": user.id   # Important so frontend can open OTP page
        }, status=200)
