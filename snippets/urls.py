from django.urls import path
from .views import SnippetCreateView, SnippetDetailView

urlpatterns = [
    path("create/snippet/", SnippetCreateView.as_view(), name="create-snippet-api"),
    path("snippet/detail/<int:id>/", SnippetDetailView.as_view(), name="snippet-detail-api")
               ]