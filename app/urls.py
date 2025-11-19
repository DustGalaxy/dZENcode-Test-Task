from django.urls import path
from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
)

app_name = "app"

urlpatterns = [
    path("comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    path("comments/<int:pk>/", CommentDetailAPIView.as_view(), name="comment-detail"),
]
