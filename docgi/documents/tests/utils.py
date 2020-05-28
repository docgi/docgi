from rest_framework.reverse import reverse


def url_list_create_collection():
    return reverse("documents:collections-list")


def url_collection_detail(collection_id):
    return reverse("documents:collections-detail", kwargs={
        "pk": collection_id
    })


def url_list_and_create_document():
    return reverse("documents:documents-list")


def url_doc_detail(doc_id):
    return reverse("documents:documents-detail", kwargs={
        "pk": doc_id
    })
