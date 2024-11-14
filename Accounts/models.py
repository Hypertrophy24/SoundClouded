from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import ASCIIUsernameValidator

class CustomUser(AbstractUser):
    spotifyURI = models.TextField(null=True, blank=True)
    username = models.CharField(
        max_length=255,
        unique=True,
        help_text='Required. 255 characters or fewer.',
        validators=[ASCIIUsernameValidator()],
        error_messages={'unique': "A user with that username already exists."},
    )