from django.urls import path

from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
    CommentPreviewAPIView,
    RegistrationView,
    user_me,
    comment_text_preview,
    health_check,
)

urlpatterns = [
    path("comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("comments/preview/", CommentPreviewAPIView.as_view(), name="comment-preview"),
    path("comments/<int:pk>/", CommentDetailAPIView.as_view(), name="comment-detail"),
    path("comments/preview-text/", comment_text_preview, name="comment-text-preview"),
    path("user/me/", user_me, name="user-me"),
    path("user/register/", RegistrationView.as_view(), name="user-register"),
    path("health/", health_check, name="health_check"),
]
