from rest_framework import permissions, status, mixins, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
import pyotp
from users.models import Users
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import UserSerializer
import random
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser

from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

    
class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
           
            return Response(
                {'detail': 'Invalid credentials or not an admin'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        

        if user.check_password(password) and user.is_superuser:
           
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_superuser': user.is_superuser,
                'email': user.email,
                'user': user.id,
                
            })

        return Response(
            {'detail': 'Invalid credentials or not an admin'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    



class AdminLogoutView(APIView):
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
        
        
class AdminUserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    
    def get_queryset(self):
        return Users.objects.filter(is_email_verified = True, role="user")

    
    @action(detail=True, methods=["post"], url_path='block')
    def block(self, request, pk=None):
        user = Users.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False  
        user.save()
        return Response({"msg": "User blocked successfully"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=["post"], url_path='unblock')
    def unblock(self, request, pk=None):
        user = Users.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True  
        user.save()
        return Response({"msg": "User unblocked successfully"}, status=status.HTTP_200_OK)
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=["post"])
    def update_role(self, request, pk=None):
        user = Users.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        role = request.data.get("role")

        if role not in ["user", "admin", "staff"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        user.role = role
        user.save()
        return Response({"msg": f"Role updated to {role} successfully"}, status=status.HTTP_200_OK)
    
    
    

class AdminStaffViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet      

):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    
    
    def get_queryset(self):
        return Users.objects.filter(role = 'staff')
    def get(self, request, *args, **kwargs):
         return self.list(request, *args, **kwargs)
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["role"] = "staff"
        is_active_val = request.data.get("is_active")
        if is_active_val is not None:
            if str(is_active_val).lower() in ['true', '1', 'yes']:
                data["is_active"] = True
            elif str(is_active_val).lower() in ['false', '0', 'no']:
                data["is_active"] = False
        
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
            
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=["post"], url_path="block")
    def block(self, request, pk=None):
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        return Response({"msg": "Staff blocked successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unblock")
    def unblock(self, request, pk=None):
        staff = self.get_object()
        staff.is_active = True
        staff.save()
        return Response({"msg": "Staff unblocked successfully"}, status=status.HTTP_200_OK)
            
class AdminGetView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    
    
    

    
    
    
    