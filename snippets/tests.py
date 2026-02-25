from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Tag, Snippet

User = get_user_model()


class BaseSnippetTest(APITestCase):
    """Shared setup: two users, one authenticated."""

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass1234")
        self.other_user = User.objects.create_user(username="bob", password="pass1234")
        self._authenticate(self.user)

    def _authenticate(self, user):
        login_url = reverse("user login api")
        resp = self.client.post(login_url, {"username": user.username, "password": "pass1234"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['data']['access']}")

    def _create_snippet(self, title="Test Snippet", note="Hello world", tag_titles=None):
        url = reverse("create-snippet-api")
        payload = {"title": title, "note": note}
        if tag_titles:
            payload["tag_titles"] = tag_titles
        return self.client.post(url, payload, format="json")


class SnippetOverviewTest(BaseSnippetTest):
    def test_empty_overview(self):
        url = reverse("snippet-overview-api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total_snippets"], 0)
        self.assertEqual(response.data["data"]["snippets"], [])

    def test_overview_only_shows_own_snippets(self):
        self._create_snippet(title="Alice's note")
        self._authenticate(self.other_user)
        self._create_snippet(title="Bob's note")
        self._authenticate(self.user)

        url = reverse("snippet-overview-api")
        response = self.client.get(url)
        self.assertEqual(response.data["data"]["total_snippets"], 1)
        self.assertEqual(response.data["data"]["snippets"][0]["title"], "Alice's note")

    def test_overview_requires_auth(self):
        self.client.credentials()
        url = reverse("snippet-overview-api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SnippetCreateTest(BaseSnippetTest):
    def test_create_snippet_without_tags(self):
        response = self._create_snippet()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["title"], "Test Snippet")
        self.assertEqual(response.data["data"]["tags"], [])

    def test_create_snippet_with_tags(self):
        response = self._create_snippet(tag_titles=["python", "django"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tag_titles = [t["title"] for t in response.data["data"]["tags"]]
        self.assertIn("python", tag_titles)
        self.assertIn("django", tag_titles)

    def test_duplicate_tag_titles_reuse_existing_tag(self):
        self._create_snippet(tag_titles=["python"])
        self._create_snippet(tag_titles=["python"])
        self.assertEqual(Tag.objects.filter(title="python").count(), 1)

    def test_created_by_is_set_to_current_user(self):
        response = self._create_snippet()
        snippet = Snippet.objects.get(pk=response.data["data"]["id"])
        self.assertEqual(snippet.created_by, self.user)

    def test_missing_required_fields_returns_400(self):
        url = reverse("create-snippet-api")
        response = self.client.post(url, {"title": "No note"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SnippetDetailTest(BaseSnippetTest):
    def setUp(self):
        super().setUp()
        resp = self._create_snippet(title="Detailed Note", tag_titles=["api"])
        self.snippet_id = resp.data["data"]["id"]

    def test_detail_returns_correct_fields(self):
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["title", "note", "tags", "created_on", "updated_on"]:
            self.assertIn(field, response.data["data"])

    def test_detail_not_accessible_by_other_user(self):
        self._authenticate(self.other_user)
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_snippet_returns_404(self):
        url = reverse("snippet-detail-api", kwargs={"id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SnippetUpdateTest(BaseSnippetTest):
    def setUp(self):
        super().setUp()
        resp = self._create_snippet(title="Original Title", tag_titles=["old-tag"])
        self.snippet_id = resp.data["data"]["id"]

    def test_update_changes_title_and_note(self):
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        payload = {"title": "Updated Title", "note": "Updated note", "tag_titles": ["new-tag"]}
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], "Updated Title")
        tag_titles = [t["title"] for t in response.data["data"]["tags"]]
        self.assertIn("new-tag", tag_titles)

    def test_update_by_other_user_returns_404(self):
        self._authenticate(self.other_user)
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        response = self.client.put(url, {"title": "Hacked", "note": "..."}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SnippetDeleteTest(BaseSnippetTest):
    def setUp(self):
        super().setUp()
        resp = self._create_snippet(title="To Be Deleted")
        self.snippet_id = resp.data["data"]["id"]

    def test_delete_removes_snippet_and_returns_remaining(self):
        self._create_snippet(title="Stays Around")
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total_snippets_remaining"], 1)
        self.assertFalse(Snippet.objects.filter(pk=self.snippet_id).exists())

    def test_delete_by_other_user_returns_404(self):
        self._authenticate(self.other_user)
        url = reverse("snippet-detail-api", kwargs={"id": self.snippet_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TagListTest(BaseSnippetTest):
    def test_tag_list_returns_all_tags(self):
        self._create_snippet(tag_titles=["python", "django"])
        url = reverse("tag-list-api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag_titles = [t["title"] for t in response.data["data"]]
        self.assertIn("python", tag_titles)
        self.assertIn("django", tag_titles)
        

class TagDetailTest(BaseSnippetTest):
    def setUp(self):
        super().setUp()
        self._create_snippet(title="First", tag_titles=["backend"])
        self._create_snippet(title="Second", tag_titles=["backend"])
        self.tag = Tag.objects.get(title="backend")

    def test_tag_detail_returns_linked_snippets(self):
        url = reverse("snippets-linked-tag", kwargs={"id": self.tag.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]["snippets"]), 2)

    def test_nonexistent_tag_returns_404(self):
        url = reverse("snippets-linked-tag", kwargs={"id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)