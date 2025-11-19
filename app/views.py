from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all top-level comments (no parent) and create new comments.
    GET: Returns all comments that are not replies
    POST: Create a new comment
    """

    queryset = Comment.objects.filter(reply__isnull=True).order_by("-created_at")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentSerializer


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific comment.
    GET: Retrieve a comment by ID
    PUT/PATCH: Update a comment
    DELETE: Delete a comment
    """

    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "POST"]:
            return CommentCreateSerializer
        return CommentSerializer


class CommentRepliesAPIView(generics.ListAPIView):
    """
    API view to list all replies to a specific comment.
    GET: Returns all replies for a given comment ID
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        comment_id = self.kwargs.get("pk")
        return Comment.objects.filter(reply=comment_id).order_by("-created_at")
