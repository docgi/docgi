from django.urls import reverse
from rest_framework import status

from docgi.documents import models
from docgi.base.tests import DocgiTestCase


def url_list_create_collection():
    return reverse("documents:collections-list")


def url_collection_detail(collection_id):
    return reverse("documents:collections-detail", kwargs={
        "pk": collection_id
    })


def url_list_and_create_document():
    return reverse("documents:documents-list")


class TestCollection(DocgiTestCase):
    def _new_collection(self, name="Collection", **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_201_CREATED)
        payload = {
            "name": name,
            **kwargs
        }
        return self.post(url_list_create_collection(), data=payload, status_code=status_code)

    def _update_collection(self, collection_id, **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_200_OK)
        payload = {**kwargs}
        return self.patch(url_collection_detail(collection_id), data=payload, status_code=status_code)

    def test_create_collection(self):
        res = self._new_collection(members=[self.member1.pk, self.member2.pk])
        self.assertFalse(res.data["private"])

    def test_create_private_collection(self):
        res = self._new_collection(private=True)
        self.assertTrue(res.data["private"])

    def test_create_duplicate_collection_name(self):
        self._new_collection()
        self._new_collection(status_code=status.HTTP_400_BAD_REQUEST)

    def test_update_collection_name_duplicate(self):
        old_collection_name = "Collection"
        self._new_collection(old_collection_name)
        res = self._new_collection(name="Diff")
        new_collection_id = res.data["id"]
        self._update_collection(collection_id=new_collection_id,
                                name=old_collection_name,
                                status_code=status.HTTP_400_BAD_REQUEST)

    def test_get_collection_per_member(self):
        # Create with member
        self._new_collection("1")
        self._new_collection("2", private=True)

        # Create with member2
        self.make_login(self.member2)
        self._new_collection("3", private=True)
        self._new_collection("4", private=True)

        # Create and get with member1
        self.make_login(self.member1)
        self._new_collection("5")
        self._new_collection("6", private=True)

        res = self.get(url_list_create_collection())
        self.assertEqual(len(res.data), 3)  # include one of creator and two of this user.

    def test_delete_collection(self):
        res = self._new_collection()
        collection_id = res.data["id"]
        self.delete(url_collection_detail(collection_id))

        _count = models.Collection.objects.filter(
            creator=self.creator, workspace_id__exact=self._workspace_name
        ).count()
        self.assertEqual(_count, 0)

    def test_non_owner_collection(self):
        res = self._new_collection()
        collection_id = res.data["id"]
        self.make_login(self.member1)
        self.delete(url_collection_detail(collection_id), status_code=status.HTTP_403_FORBIDDEN)

    def test_get_private_collection(self):
        self._new_collection()
        self._new_collection(
            name="Collection 2",
            private=True,
        )

        self.make_login(self.creator)
        res = self.get(url_list_create_collection())
        self.assertEqual(len(res.data), 2)

        self.make_login(self.member2)
        res = self.get(url_list_create_collection())
        self.assertEqual(len(res.data), 1)

        self.make_login(self.member3)
        res = self.get(url_list_create_collection())
        self.assertEqual(len(res.data), 1)

    def test_create_with_parent_none(self):
        self._new_collection(
            name="Collection 2",
            private=True,
            parent=None
        )

    def test_create_with_invalid_id_parent(self):
        self._new_collection(
            name="Collection 2",
            private=True,
            parent=-1,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class TestDocument(DocgiTestCase):
    def setUp(self) -> None:
        super().setUp()
        res = self._new_collection()
        self.collection = models.Collection.objects.get(id=res.data["id"])

    def _new_collection(self, name="Collection", **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_201_CREATED)
        payload = {
            "name": name,
            **kwargs
        }
        return self.post(url_list_create_collection(), data=payload, status_code=status_code)

    def _new_doc(self, collection_id=None, title="Doc", **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_201_CREATED)
        payload = {
            "collection": collection_id,
            "title": title,
            **kwargs
        }
        return self.post(url_list_and_create_document(), data=payload, status_code=status_code)

    def test_create_doc(self):
        self._new_doc(collection_id=self.collection.id)
