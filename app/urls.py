from django.urls import path

from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
    CommentPreviewAPIView,
)

urlpatterns = [
    path("comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("comments/preview/", CommentPreviewAPIView.as_view(), name="comment-preview"),
    path("comments/<int:pk>/", CommentDetailAPIView.as_view(), name="comment-detail"),
]
