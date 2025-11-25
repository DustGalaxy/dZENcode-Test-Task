from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField()


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

    def get_root_comment(self):
        current = self
        while current.reply is not None:
            current = current.reply
        return current


class CommentAttachment(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.URLField()
    media_type = models.CharField(max_length=50)
