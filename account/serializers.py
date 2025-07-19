from rest_framework import serializers
from account.models import CustomUser
class UserSerializers(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
    def create(self, validate_data):
        return CustomUser.objects.create_user(**validate_data)
    
    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None