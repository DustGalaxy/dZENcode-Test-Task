import bleach
from rest_framework import serializers

from .models import Comment, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = ["id"]


class CommentPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at", "updated_at", "reply", "replies"]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def get_replies(self, obj):
        """Get all replies to this comment"""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    ALLOWED_TAGS = ["a", "code", "i", "strong"]
    ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}

    class Meta:
        model = Comment
        fields = ["id", "text", "reply", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_text(self, value):
        cleaned_text = bleach.clean(
            value,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True,
        )

        cleaned_text = bleach.linkify(
            cleaned_text,
            parse_email=False,
            callbacks=[],
        )

        return cleaned_text

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
