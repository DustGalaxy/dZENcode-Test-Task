from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.core.cache import cache

from app.models import Comment
from app.serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    UserSerializer,
    CommentPreviewSerializer,
    RegistrationSerializer,
)
from app.utils import StandardResultsSetPagination


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    authentication_classes = []
    permission_classes = []


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all top-level comments (no parent) and create new comments.
    GET: Returns all comments that are not replies
    POST: Create a new comment
    """

    queryset = Comment.objects.filter(reply__isnull=True).order_by("-created_at")
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "user__username", "user__email"]
    ordering = ["-created_at"]
    search_fields = ["user__username", "user__email"]

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
        cache_key = "comment_preview_list"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def comment_text_preview(request):
    serializer = CommentCreateSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        return Response({"text": serializer.validated_data["text"]})

    return Response(serializer.errors, status=400)


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})
