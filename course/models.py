from django.db import models
from django.conf import settings
from django.utils.text import slugify
# Create your models here.


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

    def __str__(self):
        return self.title