import traceback
from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import SnippetWriteSerializer, SnippetDetailSerializer, SnippetOverviewSerializer, TagSerializer, TagDetailSerializer
from utils.permissions import IsAdminUser
from utils.custom_response import ApiResponse
from .models import Snippet, Tag
from utils.cache_utils import (
    invalidate_snippet_caches,
    invalidate_tag_caches,
    snippet_detail_key,
    snippet_list_key,
    tag_detail_key,
    tag_list_key,
)


class SnippetOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = snippet_list_key(request.user.pk)
        cached = cache.get(cache_key)
        if cached is not None:
            return ApiResponse.success(data=cached, message="Snippets retrieved from cache.")

        snippets = Snippet.objects.filter(created_by=request.user).only("id", "title")
        serializer = SnippetOverviewSerializer(snippets, many=True, context={"request": request})
        payload = {
            "total_snippets": snippets.count(),
            "snippets": serializer.data,
        }
        cache.set(cache_key, payload, timeout=settings.CACHE_TTL_SNIPPET_LIST)
        return ApiResponse.success(data=payload, message="Snippets retrieved successfully.")

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
        try:
            cache_key = snippet_detail_key(request.user.id,id)
            cached = cache.get(cache_key)
            if cached is not None:
                return ApiResponse.success(data=cached, message="Snippet retrieved from cache.")

            snippet = self._get_snippet_and_tag(id, request.user)
            serializer = SnippetDetailSerializer(snippet, context={"request": request})
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL_SNIPPET_DETAIL)
            return ApiResponse.success(data=serializer.data, message="Snippet retrieved successfully.")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))
        
    def put(self, request, id):
        try:
            snippet = self._get_snippet_and_tag(id, request.user)
            serializer = SnippetWriteSerializer(snippet, data=request.data, context={"request": request})
            if not serializer.is_valid():
                return ApiResponse.error(message="Snippet update failed.", errors=serializer.errors)

            serializer.save()
            invalidate_snippet_caches(request.user.pk, snippet_id=id)
            invalidate_tag_caches()
            return ApiResponse.success(data=serializer.data, message="Snippet updated successfully.")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))

    def delete(self, request, id):
        try:
            snippet = self._get_snippet_and_tag(id, request.user)
            snippet.delete()
            invalidate_snippet_caches(request.user.pk, snippet_id=id)
            invalidate_tag_caches()

            remaining = Snippet.objects.filter(created_by=request.user).only("id", "title")
            serializer = SnippetOverviewSerializer(remaining, many=True, context={"request": request})
            payload = {
                "total_snippets_remaining": remaining.count(),
                "snippets": serializer.data,
            }
            return ApiResponse.success(message="Snippet deleted successfully.", data=payload)
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))
    

class TagListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cache_key = tag_list_key()
            cached = cache.get(cache_key)
            if cached is not None:
                return ApiResponse.success(data=cached, message="Tags retrieved from cache.")

            tags = Tag.objects.all().order_by("title") #getting tags and count of each snippets in a tag
            serializer = TagSerializer(tags, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL_TAG_LIST)
            return ApiResponse.success(data=serializer.data, message="Tags retrieved successfully.")
        except Exception as e:
            return ApiResponse.exception(message=str(e), errors=str(traceback.format_exc()))
        

class TagDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        cache_key = tag_detail_key(id, request.user.id)
        cached = cache.get(cache_key)
        if cached is not None:
            return ApiResponse.success(data=cached, message=f"Snippets associaed to Tag '{cached.get('title').title()}' retrieved successfully.")

        tag = get_object_or_404(
            Tag.objects.prefetch_related(  #writing this logic inside the get object or 404 because serilizer expect tag object
                Prefetch(
                    "snippets",
                    queryset=Snippet.objects.filter(created_by=request.user)
                )
            ),
            pk=id
        )
        serializer = TagDetailSerializer(tag, context={"request": request})
        cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL_TAG_DETAIL)
        return ApiResponse.success(data=serializer.data, message=f"Snippets associaed to Tag '{serializer.data.get('title').title()}' retrieved successfully.")