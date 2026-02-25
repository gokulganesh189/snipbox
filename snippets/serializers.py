from rest_framework import serializers

from .models import Snippet, Tag


class TagMinimalSerializer(serializers.ModelSerializer):
    """Lightweight representation used inside snippet payloads."""

    class Meta:
        model = Tag
        fields = ["id", "title"]


class SnippetDetailSerializer(serializers.ModelSerializer):
    tags = TagMinimalSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Snippet
        fields = [
            "id",
            "title",
            "note",
            "tags",
            "created_by",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["created_on", "updated_on", "created_by"]


class SnippetWriteSerializer(serializers.ModelSerializer):
    """
    Handles creation and updates.  Tags are accepted as a list of title strings
    so callers never have to look up or pre-create tag PKs.
    """

    tag_titles = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of tag titles (strings). Tags are created if they don't exist.",
    )

    class Meta:
        model = Snippet
        fields = ["title", "note", "tag_titles"]

    def _resolve_tags(self, tag_titles):
        """
        For each title: fetch the existing tag or create a new one.
        This is intentionally a single loop with get_or_create so we never
        end up with duplicate tags from race conditions (the DB unique constraint
        acts as the final guard).
        """
        tags = []
        for raw_title in tag_titles:
            title = raw_title.strip().lower()
            if not title:
                continue
            tag, _ = Tag.objects.get_or_create(title=title)
            tags.append(tag)
        return tags

    def create(self, validated_data):
        tag_titles = validated_data.pop("tag_titles", [])
        snippet = Snippet.objects.create(**validated_data)
        if tag_titles:
            snippet.tags.set(self._resolve_tags(tag_titles))
        return snippet

    def update(self, instance, validated_data):
        tag_titles = validated_data.pop("tag_titles", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_titles is not None:
            instance.tags.set(self._resolve_tags(tag_titles))
        return instance

    def to_representation(self, instance):
        # After write operations, return the full detail view.
        return SnippetDetailSerializer(instance, context=self.context).data

