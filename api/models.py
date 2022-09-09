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

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, default=None)

    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh), str(refresh.access_token)


class Token(models.Model):
    access_token = models.CharField(max_length=500, null=True)
    refresh_token = models.CharField(max_length=500, null=True)

    # user_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
