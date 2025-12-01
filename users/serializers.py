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

        user = Users.objects.create_user(**validated_data)

        
        if groups:
            user.groups.set(groups)

        if permissions:
            user.user_permissions.set(permissions)

        return user
