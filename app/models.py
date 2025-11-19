from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    text = models.TextField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    reply = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )
