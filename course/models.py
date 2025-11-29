from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    active = models.BooleanField(default=True)

    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'staff'},
        related_name='courses_assigned',
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  

    def __str__(self):
        return self.title



class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='module_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Topic(models.Model):
    module = models.ForeignKey(Module, related_name='topics', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='topic_images/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'staff'},
        related_name='topics_assigned',
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"



class Video(models.Model):
    topic = models.ForeignKey(Topic, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    duration = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.topic.title})"


class Document(models.Model):
    topic = models.ForeignKey(Topic, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='topic_documents/')
    title = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
