from django.urls import path
from .views import SnippetCreateView, SnippetDetailView, TagListView, TagDetailView, SnippetOverviewView

urlpatterns = [
    path("snippet/overview/", SnippetOverviewView.as_view(), name='snippet-overview-api'),
    path("snippet/create/", SnippetCreateView.as_view(), name="create-snippet-api"),
    path("snippet/<int:id>/", SnippetDetailView.as_view(), name="snippet-detail-api"),

    path("tags/", TagListView.as_view(), name="tag-list-api"),
    path("tags/<int:id>/", TagDetailView.as_view(), name="snippets-linked-tag")
               ]