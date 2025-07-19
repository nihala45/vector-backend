from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializers  
from rest_framework_simplejwt.tokens import RefreshToken  
from .models import CustomUser

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








