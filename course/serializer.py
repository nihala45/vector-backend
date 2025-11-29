from rest_framework import serializers
from .models import Course, Module, Topic, Video, Document



class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'slug': {'read_only': True},
        }

    def validate_title(self, value):
        course_id = self.instance.id if self.instance else None
        if Course.objects.exclude(id=course_id).filter(title=value).exists():
            raise serializers.ValidationError("Course with this title already exists.")
        return value



class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def validate_title(self, value):
        module_id = self.instance.id if self.instance else None
        course_id = self.initial_data.get("course")  # foreign key

        if Module.objects.exclude(id=module_id).filter(course_id=course_id, title=value).exists():
            raise serializers.ValidationError("A module with this title already exists in this course.")
        return value



class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def validate_title(self, value):
        topic_id = self.instance.id if self.instance else None
        module_id = self.initial_data.get("module")

        if Topic.objects.exclude(id=topic_id).filter(module_id=module_id, title=value).exists():
            raise serializers.ValidationError("A topic with this title already exists in this module.")
        return value



class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

    def validate_title(self, value):
        video_id = self.instance.id if self.instance else None
        topic_id = self.initial_data.get("topic")

        # Only if you want unique titles inside the same topic
        if Video.objects.exclude(id=video_id).filter(topic_id=topic_id, title=value).exists():
            raise serializers.ValidationError("A video with this title already exists in this topic.")
        return value


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

    def validate_title(self, value):
        document_id = self.instance.id if self.instance else None
        topic_id = self.initial_data.get("topic")

        # If you want unique document titles inside topic
        if Document.objects.exclude(id=document_id).filter(topic_id=topic_id, title=value).exists():
            raise serializers.ValidationError("A document with this title already exists in this topic.")
        return value
