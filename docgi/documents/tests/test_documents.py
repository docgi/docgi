from rest_framework import status

from docgi.base.tests import DocgiTestCase

from .. import models
from .utils import *


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

    def _new_doc(self, collection_id=None, name="Doc", **kwargs):
        status_code = kwargs.pop("status_code", status.HTTP_201_CREATED)
        payload = {
            "collection": str(collection_id),
            "name": name,
            **kwargs
        }
        return self.post(url_list_and_create_document(), data=payload, status_code=status_code)

    def test_create_doc(self):
        res = self._new_doc(collection_id=self.collection.id, name="New")
        self.assertEqual(len(res.data["contributors"]), 1)
        self.assertIsNotNone(res.data["creator"])
        self.assertIsNotNone(res.data["last_update_by"])

    def test_update_doc(self):
        res = self._new_doc(
            collection_id=self.collection.id,
            name="New",
            json_content="json_content",
            html_content="html_content"
        )

        payload_update = {
            "json_content": "diff_json_content",
            "html_content": "diff_html_content"
        }

        self.put(url_doc_detail(res.data["id"]), payload_update, status_code=status.HTTP_200_OK)

    def test_create_empty_name_doc(self):
        self._new_doc(name="", collection_id=self.collection.id)

    def test_update_with_other_user(self):
        res = self._new_doc(
            collection_id=self.collection.id,
            name="New",
            json_content="json_content",
            html_content="html_content"
        )

        payload_update = {
            "json_content": "diff_json_content",
            "html_content": "diff_html_content"
        }
        self.make_login(self.member1)
        res = self.put(url_doc_detail(res.data["id"]), payload_update, status_code=status.HTTP_200_OK)
        self.assertEqual(len(res.data["contributors"]), 2)
        self.assertEqual(res.data["last_update_by"]["id"], self.member1.pk)
