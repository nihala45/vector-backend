from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'slug': {'read_only': True},   # slug auto-generated
        }

    def validate_title(self, value):
        course_id = self.instance.id if self.instance else None
        if Course.objects.exclude(id=course_id).filter(title=value).exists():
            raise serializers.ValidationError("Course with this title already exists.")
        return value

    def create(self, validated_data):
        # slug auto generation handled in model.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # auto update slug when title changes
        return super().update(instance, validated_data)
