from django.test import TestCase, Client
from rest_framework import status


class DocgiTestCase(TestCase):
    def get(self, path: str, status_code=status.HTTP_200_OK, **kwargs):
        res = self.client.get(path=path, **kwargs)
        self.assertEqual(res.status_code, status_code)
        return res

    def post(self, path: str, data: dict, status_code=status.HTTP_201_CREATED, **kwargs):
        res = self.client.post(path=path, data=data, **kwargs)
        self.assertEqual(res.status_code, status_code)
        return res

    def put(self, path: str, data: dict, status_code=status.HTTP_200_OK, **kwargs):
        res = self.client.put(path=path, data=data, **kwargs)
        self.assertEqual(res.status_code, status_code)
        return res

    def patch(self, path: str, data: dict, status_code=status.HTTP_200_OK, **kwargs):
        res = self.client.patch(path=path, data=data, **kwargs)
        self.assertEqual(res.status_code, status_code)
        return res
