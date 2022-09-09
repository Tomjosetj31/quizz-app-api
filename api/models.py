from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin

from rest_framework_simplejwt.tokens import RefreshToken


from .managers import UserManager

# Create your models here.


class User(AbstractUser, PermissionsMixin):

    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    accepted_terms_at = models.DateTimeField(auto_now_add=True)

    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
