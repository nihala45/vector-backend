from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, phone=None, password=None, email_otp=None, role="user", **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            phone=phone,
            email_otp=email_otp,
            role=role,                   # keep role as passed
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, username, phone=None, password=None, **extra_fields):

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(
            email=email,
            username=username,
            phone=phone,
            password=password,
            role="admin",
            **extra_fields
        )



class Users(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )

    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)   
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
