import io
import os
from PIL import Image
from django.core.files.base import ContentFile
import bleach
from rest_framework import serializers
import cloudinary.uploader

from .models import Comment, User, CommentAttachment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = ["id"]


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class CommentPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "text",
            "created_at",
            "updated_at",
            "reply",
            "replies",
            "attachments",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user", "attachments"]

    def get_attachments(self, obj):
        return [
            {"id": a.id, "file": a.file, "media_type": a.media_type}
            for a in obj.attachments.all()
        ]

    def get_replies(self, obj):
        """Get all replies to this comment"""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    ALLOWED_TAGS = ["a", "code", "i", "strong", "p", "br", "em", "b"]
    ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}

    attachments = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Comment
        fields = ["id", "text", "reply", "created_at", "updated_at", "attachments"]
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

    def validate(self, attrs):
        attachments = attrs.get("attachments", [])
        for i, file in enumerate(attachments):
            # Check size (100KB)
            if file.size > 100 * 1024:
                raise serializers.ValidationError(
                    f"File {file.name} is too big. Max 100KB."
                )

            # Check extension
            ext = os.path.splitext(file.name)[1].lower()
            if ext == ".txt":
                continue
            elif ext in [".jpg", ".jpeg", ".png", ".gif"]:
                # Process image
                file = self._process_image(file, ext)
                attachments[i] = file
            else:
                raise serializers.ValidationError(
                    f"File {file.name} has invalid format. Only TXT, JPG, PNG, GIF allowed."
                )

        attrs["attachments"] = attachments
        return attrs

    def _process_image(self, file, ext):
        try:
            image = Image.open(file)

            # Check dimensions
            if image.width > 320 or image.height > 240:
                image.thumbnail((320, 240))

                output = io.BytesIO()
                # Determine format from extension or original format
                img_format = (
                    image.format if image.format else ext.replace(".", "").upper()
                )
                if img_format == "JPG":
                    img_format = "JPEG"

                image.save(output, format=img_format)
                output.seek(0)

                return ContentFile(output.read(), name=file.name)

            return file
        except Exception as e:
            raise serializers.ValidationError(f"Invalid image file: {file.name}")

    def create(self, validated_data):
        attachments_data = validated_data.pop("attachments", [])
        user = self.context["request"].user
        validated_data["user"] = user
        comment = super().create(validated_data)

        for file in attachments_data:
            # Determine media type based on extension since content_type might be generic for ContentFile
            ext = os.path.splitext(file.name)[1].lower()
            media_type = "image" if ext in [".jpg", ".jpeg", ".png", ".gif"] else "file"

            cloudinary_file = cloudinary.uploader.upload(
                file,
                resource_type="auto",
            )
            file_url = cloudinary_file["secure_url"]

            CommentAttachment.objects.create(
                comment=comment, file=file_url, media_type=media_type
            )
        comment.attachments.set(CommentAttachment.objects.filter(comment=comment))
        return comment
