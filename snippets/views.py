import traceback
from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import SnippetWriteSerializer, SnippetDetailSerializer
from utils.permissions import IsAdminUser
from utils.custom_response import ApiResponse
from .models import Snippet
from utils.cache_utils import (
    invalidate_snippet_caches,
    invalidate_tag_caches,
    snippet_detail_key,
    snippet_list_key,
    tag_detail_key,
    tag_list_key,
)


class SnippetCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SnippetWriteSerializer(data=request.data, context={"request": request})
            if not serializer.is_valid():
                return ApiResponse.error(message="Snippet creation failed.", errors=serializer.errors)

            snippet = serializer.save(created_by=request.user)
            invalidate_snippet_caches(request.user.pk, snippet.id)
            invalidate_tag_caches()
            return ApiResponse.created(data=serializer.data, message="Snippet created successfully.")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))

class SnippetDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def _get_snippet_and_tag(self, id, user):
        return Snippet.objects.select_related('created_by').prefetch_related('tags').get(id=id, created_by=user)

    def get(self, request, id):
        cache_key = snippet_detail_key(request.user.id,id)
        cached = cache.get(cache_key)
        if cached is not None:
            return ApiResponse.success(data=cached, message="Snippet retrieved from cache.")

        snippet = self._get_snippet_and_tag(id, request.user)
        serializer = SnippetDetailSerializer(snippet, context={"request": request})
        cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL_SNIPPET_DETAIL)
        return ApiResponse.success(data=serializer.data, message="Snippet retrieved successfully.")
