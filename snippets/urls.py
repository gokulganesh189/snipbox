from django.urls import path
from .views import SnippetCreateView, SnippetDetailView

urlpatterns = [
    path("snippet/create/", SnippetCreateView.as_view(), name="create-snippet-api"),
    path("snippet/<int:id>/", SnippetDetailView.as_view(), name="snippet-detail-api")
               ]