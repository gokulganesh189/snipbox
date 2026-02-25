from django.core.cache import cache


def snippet_list_key(user_id: int) -> str:
    return f"snippets:list:user:{user_id}"


def snippet_detail_key(user_id: int, snippet_id: int) -> str:
    return f"snippets:detail:user:{user_id}:{snippet_id}"


def tag_list_key() -> str:
    return "tags:list"


def tag_detail_key(tag_id: int, user_id: int) -> str:
    return f"tags:detail:{tag_id}:{user_id}"


def invalidate_snippet_caches(user_id: int, snippet_id: int | None = None) -> None:
    keys = [snippet_list_key(user_id)]
    if snippet_id is not None:
        keys.append(snippet_detail_key(user_id, snippet_id))
    cache.delete_many(keys)


def invalidate_tag_caches(tag_id: int | None = None, user_id: int | None = None) -> None:
    keys = [tag_list_key()]
    if tag_id is not None and user_id is not None: # user and tag specific key is deleted
        keys.append(tag_detail_key(tag_id, user_id))
    cache.delete_many(keys)
    pattern = "tags:detail:*"
    if hasattr(cache, "iter_keys"): #delete all keys starts with pattern
        for key in cache.iter_keys(pattern):
            cache.delete(key)