from django.urls import reverse
from django.utils.functional import cached_property
from rest_framework import status

from apps.documents import models
from apps.utils.tests import DocgiTestCase


class TestCollection(DocgiTestCase):
    @cached_property
    def url_create_collection(self):
        return reverse("documents:collections-list")

    def _url_collection_detail(self, collection_id):
        return reverse("documents:collections-detail", kwargs={
            "pk": collection_id
        })

    def _new_collection(self, name="Collection", **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_201_CREATED)
        payload = {
            "name": name,
            **kwargs
        }
        return self.post(self.url_create_collection, data=payload, status_code=status_code)

    def _update_collection(self, collection_id, **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_200_OK)
        payload = {**kwargs}
        url_collection_detail = self._url_collection_detail(collection_id)
        return self.patch(url_collection_detail, data=payload, status_code=status_code)

    def test_create_collection(self):
        res = self._new_collection(members=[self.member1.pk, self.member2.pk])
        self.assertEqual(len(res.data["members"]), 3)
        self.assertFalse(res.data["private"])

    def test_create_private_collection(self):
        res = self._new_collection(private=True)
        self.assertTrue(res.data["private"])

    def test_create_duplicate_collection_name(self):
        self._new_collection()
        self._new_collection(status_code=status.HTTP_400_BAD_REQUEST)

    def test_create_no_member(self):
        res = self._new_collection()
        self.assertEqual(len(res.data["members"]), 1)

    def test_update_collection_name_duplicate(self):
        old_collection_name = "Collection"
        self._new_collection(old_collection_name)
        res = self._new_collection(name="Diff")
        new_collection_id = res.data["id"]
        self._update_collection(collection_id=new_collection_id,
                                name=old_collection_name,
                                status_code=status.HTTP_400_BAD_REQUEST)

    def test_make_sure_members_is_readonly(self):
        res = self._new_collection()
        collection_id = res.data["id"]
        res = self._update_collection(collection_id=collection_id,
                                      members=[self.member1.id, self.member2.id])
        self.assertEqual(len(res.data["members"]), 1)  # Only creator

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

        res = self.get(self.url_create_collection)
        self.assertEqual(len(res.data), 3)  # one of creator

    def test_delete_collection(self):
        res = self._new_collection()
        collection_id = res.data["id"]
        url_collection_detail = self._url_collection_detail(collection_id)
        self.delete(url_collection_detail)

        _count = models.Collection.objects.filter(
            creator=self.creator, workspace_id__exact=self._workspace_name
        ).count()
        self.assertEqual(_count, 0)

    def test_non_owner_collection(self):
        res = self._new_collection()
        collection_id = res.data["id"]
        url_collection_detail = self._url_collection_detail(collection_id)
        self.make_login(self.member1)
        self.delete(url_collection_detail, status_code=status.HTTP_403_FORBIDDEN)
