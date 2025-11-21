from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from app.serializers import CommentPreviewSerializer


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


class CommentPreviewAPIView(generics.ListAPIView):
    """
    API view to list all top-level comments (no parent) with Redis caching.
    GET: Returns all comments that are not replies
    Cache TTL: 5 minutes
    """

    queryset = Comment.objects.filter(reply__isnull=True).order_by("-created_at")
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommentPreviewSerializer

    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        from rest_framework.response import Response

        cache_key = "comment_preview_list"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response
