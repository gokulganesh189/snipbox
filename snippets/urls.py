from django.urls import path
from .views import SnippetCreateView

urlpatterns = [path("create/snippet/", SnippetCreateView.as_view(), name="create-snippet"),]