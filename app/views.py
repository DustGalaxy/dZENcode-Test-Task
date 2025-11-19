from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all top-level comments (no parent) and create new comments.
    GET: Returns all comments that are not replies
    POST: Create a new comment
    """

    queryset = Comment.objects.filter(reply__isnull=True).order_by("-created_at")
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "POST"]:
            return CommentCreateSerializer
        return CommentSerializer
