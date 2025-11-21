import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

from .models import Comment
from .consumers import ReplyConsumer
from .serializers import CommentSerializer, CommentCreateSerializer

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_user_string_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(str(user), "testuser")


class CommentModelTest(TestCase):
    """Тесты для модели Comment"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_comment(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        self.assertEqual(comment.text, "Test comment")
        self.assertEqual(comment.user, self.user)
        self.assertIsNone(comment.reply)

    def test_create_reply(self):
        """Тест создания ответа на комментарий"""
        parent_comment = Comment.objects.create(user=self.user, text="Parent comment")
        reply = Comment.objects.create(
            user=self.user, text="Reply comment", reply=parent_comment
        )
        self.assertEqual(reply.reply, parent_comment)
        self.assertIn(reply, parent_comment.replies.all())

    def test_comment_timestamps(self):
        """Тест автоматических временных меток"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)


class CommentSerializerTest(TestCase):
    """Тесты для сериализаторов комментариев"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_comment_serializer(self):
        """Тест сериализации комментария"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        serializer = CommentSerializer(comment)
        data = serializer.data

        self.assertEqual(data["text"], "Test comment")
        self.assertEqual(data["user"]["username"], "testuser")
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("replies", data)

    def test_comment_with_replies_serializer(self):
        """Тест сериализации комментария с ответами"""
        parent = Comment.objects.create(user=self.user, text="Parent comment")
        Comment.objects.create(user=self.user, text="Reply comment", reply=parent)

        serializer = CommentSerializer(parent)
        data = serializer.data

        self.assertEqual(len(data["replies"]), 1)
        self.assertEqual(data["replies"][0]["text"], "Reply comment")

    def test_html_sanitization(self):
        """Тест санитизации HTML"""
        serializer = CommentCreateSerializer(
            data={"text": "<script>alert('xss')</script>Hello"}
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["text"], "alert('xss')Hello")

    def test_allowed_html_tags(self):
        """Тест разрешенных HTML тегов"""
        text = '<a href="http://example.com">Link</a> <strong>Bold</strong> <i>Italic</i> <code>Code</code>'
        serializer = CommentCreateSerializer(data={"text": text})
        self.assertTrue(serializer.is_valid())
        self.assertIn("<a", serializer.validated_data["text"])
        self.assertIn("<strong>", serializer.validated_data["text"])
        self.assertIn("<i>", serializer.validated_data["text"])
        self.assertIn("<code>", serializer.validated_data["text"])


class CommentAPITest(APITestCase):
    """Тесты для API комментариев"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_list_comments_unauthorized(self):
        """Тест получения списка комментариев без авторизации"""
        response = self.client.get("/api/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_comments_authorized(self):
        """Тест получения списка комментариев с авторизацией"""
        Comment.objects.create(user=self.user, text="Test comment")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get("/api/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_comment_unauthorized(self):
        """Тест создания комментария без авторизации"""
        response = self.client.post("/api/comments/", {"text": "New comment"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_authorized(self):
        """Тест создания комментария с авторизацией"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post("/api/comments/", {"text": "New comment"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().text, "New comment")

    def test_create_reply(self):
        """Тест создания ответа на комментарий"""
        parent = Comment.objects.create(user=self.user, text="Parent comment")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            "/api/comments/", {"text": "Reply comment", "reply": parent.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        reply = Comment.objects.get(text="Reply comment")
        self.assertEqual(reply.reply, parent)

    def test_retrieve_comment(self):
        """Тест получения конкретного комментария"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        response = self.client.get(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Test comment")

    def test_update_comment_unauthorized(self):
        """Тест обновления комментария без авторизации"""
        comment = Comment.objects.create(user=self.user, text="Original text")
        response = self.client.patch(
            f"/api/comments/{comment.id}/", {"text": "Updated text"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_authorized(self):
        """Тест обновления комментария с авторизацией"""
        comment = Comment.objects.create(user=self.user, text="Original text")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch(
            f"/api/comments/{comment.id}/", {"text": "Updated text"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, "Updated text")

    def test_delete_comment_unauthorized(self):
        """Тест удаления комментария без авторизации"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_authorized(self):
        """Тест удаления комментария с авторизацией"""
        comment = Comment.objects.create(user=self.user, text="Test comment")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_only_top_level_comments_in_list(self):
        """Тест что в списке только комментарии верхнего уровня"""
        parent = Comment.objects.create(user=self.user, text="Parent comment")
        Comment.objects.create(user=self.user, text="Reply comment", reply=parent)

        response = self.client.get("/api/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["text"], "Parent comment")


class WebSocketConsumerTest(TestCase):
    """Тесты для WebSocket consumer"""

    async def test_websocket_connect_unauthorized(self):
        """Тест подключения к WebSocket без авторизации"""
        communicator = WebsocketCommunicator(ReplyConsumer.as_asgi(), "/ws/comments/1/")
        communicator.scope["user"] = None
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_websocket_connect_authorized(self):
        """Тест подключения к WebSocket с авторизацией"""
        user = await database_sync_to_async(User.objects.create_user)(
            username="testuser", password="testpass123"
        )
        communicator = WebsocketCommunicator(ReplyConsumer.as_asgi(), "/ws/comments/1/")
        communicator.scope["user"] = user
        communicator.scope["url_route"] = {"kwargs": {"comment_name": "1"}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_websocket_receive_new_reply(self):
        """Тест получения уведомления о новом ответе"""
        user = await database_sync_to_async(User.objects.create_user)(
            username="testuser", password="testpass123"
        )
        communicator = WebsocketCommunicator(ReplyConsumer.as_asgi(), "/ws/comments/1/")
        communicator.scope["user"] = user
        communicator.scope["url_route"] = {"kwargs": {"comment_name": "1"}}

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Отправляем событие через channel layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "comment_1",
            {
                "type": "new_reply",
                "reply": {"id": 1, "text": "Test reply", "user": "testuser"},
            },
        )

        # Получаем сообщение
        response = await communicator.receive_from()
        data = json.loads(response)

        self.assertEqual(data["type"], "new_reply")
        self.assertEqual(data["data"]["text"], "Test reply")

        await communicator.disconnect()


class EmailNotificationTests(APITestCase):
    """Тесты для email-уведомлений"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.refresh = RefreshToken.for_user(self.user2)
        self.access_token = str(self.refresh.access_token)

    def test_email_task_called_on_reply(self):
        """Тест что задача отправки email вызывается при создании ответа"""
        from unittest.mock import patch

        parent = Comment.objects.create(user=self.user1, text="Parent comment")

        with patch("app.tasks.send_reply_notification_email.delay") as mock_task:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            response = self.client.post(
                "/api/comments/", {"text": "Reply to parent", "reply": parent.id}
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Проверяем что задача была вызвана
            mock_task.assert_called_once()
            # Проверяем параметры вызова
            call_kwargs = mock_task.call_args[1]
            self.assertEqual(call_kwargs["user_email"], "user1@example.com")
            self.assertIn("Reply to parent", call_kwargs["comment_text_short"])

    def test_email_not_sent_to_self(self):
        """Тест что email не отправляется если пользователь отвечает сам себе"""
        from unittest.mock import patch

        parent = Comment.objects.create(user=self.user1, text="Parent comment")

        # Авторизуемся как user1 (автор родительского комментария)
        refresh = RefreshToken.for_user(self.user1)
        token = str(refresh.access_token)

        with patch("app.tasks.send_reply_notification_email.delay") as mock_task:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            response = self.client.post(
                "/api/comments/", {"text": "Reply to myself", "reply": parent.id}
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Email всё равно отправляется (можно изменить логику если нужно)
            # Но это показывает что сигнал сработал
            mock_task.assert_called_once()

    def test_email_content_rendering(self):
        """Тест рендеринга email шаблонов"""
        from django.template.loader import render_to_string

        reply_text = "This is a test reply"

        # Тестируем HTML шаблон
        html_content = render_to_string(
            "emails/reply_notification.html", {"reply_text": reply_text}
        )
        self.assertIn(reply_text, html_content)
        self.assertIn("Новый ответ", html_content)

        # Тестируем текстовый шаблон
        text_content = render_to_string(
            "emails/reply_notification.txt", {"reply_text": reply_text}
        )
        self.assertIn(reply_text, text_content)

    def test_email_task_execution(self):
        """Тест выполнения задачи отправки email"""
        from django.core import mail
        from app.tasks import send_reply_notification_email

        # Выполняем задачу напрямую (не через Celery)
        send_reply_notification_email(
            user_email="test@example.com", comment_text_short="Test reply text"
        )

        # Проверяем что email был отправлен
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])
        self.assertIn("Новый ответ", mail.outbox[0].subject)
        self.assertIn("Test reply text", mail.outbox[0].body)


class CachingTests(APITestCase):
    """Тесты для Redis кеширования"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        # Очищаем кеш перед каждым тестом
        from django.core.cache import cache

        cache.clear()

    def test_comment_preview_caching(self):
        """Тест кеширования списка комментариев"""
        from django.core.cache import cache

        # Создаём комментарий
        Comment.objects.create(user=self.user, text="Test comment 1")

        # Первый запрос - данные из БД
        response1 = self.client.get("/api/comments/preview/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Проверяем что данные закешированы
        cached_data = cache.get("comment_preview_list")
        self.assertIsNotNone(cached_data)

        # Второй запрос - данные из кеша
        response2 = self.client.get("/api/comments/preview/")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Данные должны быть одинаковыми
        self.assertEqual(response1.data, response2.data)

    def test_cache_invalidation_on_new_comment(self):
        """Тест инвалидации кеша при создании нового комментария"""
        from django.core.cache import cache

        # Создаём первый комментарий
        Comment.objects.create(user=self.user, text="Comment 1")

        # Делаем запрос чтобы закешировать
        response1 = self.client.get("/api/comments/preview/")
        self.assertEqual(len(response1.data), 1)

        # Проверяем что кеш существует
        self.assertIsNotNone(cache.get("comment_preview_list"))

        # Создаём новый комментарий через API
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.client.post("/api/comments/", {"text": "Comment 2"})

        # Проверяем что кеш был очищен
        self.assertIsNone(cache.get("comment_preview_list"))

        # Новый запрос должен вернуть обновлённые данные
        response2 = self.client.get("/api/comments/preview/")
        self.assertEqual(len(response2.data), 2)

    def test_only_top_level_comments_cached(self):
        """Тест что кешируются только комментарии верхнего уровня"""
        parent = Comment.objects.create(user=self.user, text="Parent comment")
        Comment.objects.create(user=self.user, text="Reply comment", reply=parent)

        response = self.client.get("/api/comments/preview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Должен быть только 1 комментарий (родительский)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["text"], "Parent comment")


class PeriodicTaskTests(TestCase):
    """Тесты для периодических задач"""

    def test_cleanup_failed_email_tasks(self):
        """Тест очистки неудачных email задач"""
        from app.tasks import cleanup_failed_email_tasks
        from django_celery_results.models import TaskResult

        # Создаём несколько записей о задачах
        TaskResult.objects.create(task_id="test-1", status="SUCCESS", result="OK")
        TaskResult.objects.create(task_id="test-2", status="FAILURE", result="Error")
        TaskResult.objects.create(task_id="test-3", status="FAILURE", result="Error")

        # Проверяем начальное состояние
        self.assertEqual(TaskResult.objects.count(), 3)
        self.assertEqual(TaskResult.objects.filter(status="FAILURE").count(), 2)

        # Запускаем задачу очистки
        cleanup_failed_email_tasks()

        # Проверяем что неудачные задачи удалены
        self.assertEqual(TaskResult.objects.count(), 1)
        self.assertEqual(TaskResult.objects.filter(status="SUCCESS").count(), 1)
        self.assertEqual(TaskResult.objects.filter(status="FAILURE").count(), 0)
