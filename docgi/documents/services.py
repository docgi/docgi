from posixpath import join as urljoin

from . import models

CLIENT_PUBLIC_PATH = "p/c"  # Client side need implement this route


def build_public_collection_url(collection: models.Collection, request):
    if collection.public is True:
        headers = request.headers
        origin = headers.get("origin", "")
        if not origin:
            return ""
        return urljoin(origin, CLIENT_PUBLIC_PATH, str(collection.id))
    return ""
