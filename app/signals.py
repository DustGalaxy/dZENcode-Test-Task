from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Comment
from .serializers import CommentSerializer


@receiver(post_save, sender=Comment)
def notify_reply_created(sender, instance, created, **kwargs):
    """
    Отправляет WebSocket уведомление при создании ответа на комментарий
    """
    if created and instance.reply is not None:
        root_comment = get_root_comment(instance)
        channel_layer = get_channel_layer()
        serialized_reply = CommentSerializer(instance).data

        group_name = f"comment_{root_comment.id}"
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "new_reply", "reply": serialized_reply}
        )


def get_root_comment(comment):
    current = comment.reply
    while current.reply is not None:
        current = current.reply
    return current
