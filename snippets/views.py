import traceback
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import SnippetWriteSerializer
from utils.permissions import IsAdminUser
from utils.custom_response import ApiResponse
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
        serializer = SnippetWriteSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return ApiResponse.error(message="Snippet creation failed.", errors=serializer.errors)

        serializer.save(created_by=request.user)
        invalidate_snippet_caches(request.user.pk)
        invalidate_tag_caches()
        return ApiResponse.created(data=serializer.data, message="Snippet created successfully.")

