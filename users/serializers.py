from rest_framework import serializers
from .models import Users

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):

        
        groups = validated_data.pop("groups", None)
        permissions = validated_data.pop("user_permissions", None)

       
        password = validated_data.pop("password", None)

        
        user = Users(**validated_data)

        if password:
            user.set_password(password)

        user.save()

        # Now assign many-to-many properly
        if groups is not None:
            user.groups.set(groups)

        if permissions is not None:
            user.user_permissions.set(permissions)

        return user
