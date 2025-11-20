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
