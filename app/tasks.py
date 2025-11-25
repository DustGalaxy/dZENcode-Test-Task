from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django_celery_results.models import TaskResult

from comments_api.celery import app
from app.exceptions import EmailSendingError


@app.task(autoretry_for=(EmailSendingError,), max_retries=3, retry_backoff=True)
def send_reply_notification_email(*args, **kwargs):
    user_email = kwargs.get("user_email")
    comment_text_short = kwargs.get("comment_text_short")

    if not user_email or not comment_text_short:
        raise ValueError("User email or comment text short is not provided")

    html_content = render_to_string(
        "emails/reply_notification.html", {"reply_text": comment_text_short}
    )
    text_content = render_to_string(
        "emails/reply_notification.txt", {"reply_text": comment_text_short}
    )

    email = EmailMultiAlternatives(
        subject="Новый ответ на ваш комментарий",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[user_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


@app.task
def cleanup_failed_email_tasks():
    failed_tasks = TaskResult.objects.filter(status="FAILURE")
    for task in failed_tasks:
        task.delete()
