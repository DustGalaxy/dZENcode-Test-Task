from django.urls import path
from .views import (
    CommentListCreateAPIView,
    CommentDetailAPIView,
    # CommentRepliesAPIView,
)

app_name = "app"

urlpatterns = [
    # List all top-level comments and create new comments
    path("comments/", CommentListCreateAPIView.as_view(), name="comment-list-create"),
    # Retrieve, update, or delete a specific comment
    path("comments/<int:pk>/", CommentDetailAPIView.as_view(), name="comment-detail"),
    # List all replies to a specific comment
    # path(
    #     "comments/<int:pk>/replies/",
    #     CommentRepliesAPIView.as_view(),
    #     name="comment-replies",
    # ),
]
