from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from app.models import Comment


@receiver(post_save, sender=Comment)
def notify_reply_created(sender, instance, created, **kwargs):
    """
    Очищает кэш при создании нового корневого комментария
    """
    if created and instance.reply is None:
        cache.delete("comment_preview_list")
