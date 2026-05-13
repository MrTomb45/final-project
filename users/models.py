import random

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from django.core.files.base import ContentFile
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from .managers import UserManager
from .utils import generate_avatar


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    github_url = models.URLField(max_length=200, unique=True, null=True, blank=True)
    about = models.TextField(max_length=256, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorites = models.ManyToManyField(
        "projects.Project", blank=True, related_name="interested_users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar = generate_avatar(self.name[0].upper())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"
