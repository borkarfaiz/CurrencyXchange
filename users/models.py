from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Default user for CurrencyXchange.
    """
    profile_pic = models.FileField(null=True, upload_to="profile_pic/%Y/%m/%d")