from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title


class Snippet(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    note = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="snippets",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="snippets")

    class Meta:
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.created_by.username})"