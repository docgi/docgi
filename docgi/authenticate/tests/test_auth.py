from django.core import mail
from django.urls import reverse
from rest_framework import status

from docgi.base.tests import DocgiTestCase

url_forgot_password = reverse("auth:forgot-password")
url_reset_password = reverse("auth:reset-password")


def get_forgot_password_token(email_text: str):
    return email_text.split("?token=")[-1]


class TestAuth(DocgiTestCase):
    def test_with_invalid_email(self):
        self.token = ""
        payload = {
            "email": "notexits@email.com",
            "workspace": self.workspace.name,
            "client_origin": "test"
        }

        self.post(url_forgot_password, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

    def test_invalid_workspace_name(self):
        self.token = ""
        payload = {
            "email": self.creator.email,
            "workspace": "no-exist",
            "client_origin": "test"
        }
        self.post(url_forgot_password, data=payload, status_code=status.HTTP_400_BAD_REQUEST)

    def test_with_valid_payload(self):
        self.token = ""
        payload = {
            "email": self.creator.email,
            "workspace": self.workspace.name,
            "client_origin": "test"
        }
        self.post(url_forgot_password, data=payload)
        forgot_mail = mail.outbox.pop()

        token = get_forgot_password_token(forgot_mail.body)
        payload = {
            "password": "123123123",
            "confirm_password": "123123123",
            "token": token
        }
        self.post(url_reset_password, data=payload)

    # def test_make_sure_not_work_when_token_expire(self):
    #     simple_jwt = settings.SIMPLE_JWT
    #     simple_jwt["REFRESH_TOKEN_LIFETIME"] = timedelta(days=1000)
    #     with override_settings(SIMPLE_JWT=simple_jwt):
    #         self.token = ""
    #         payload = {
    #             "email": self.creator.email,
    #             "workspace": self.workspace.name,
    #             "client_origin": "test"
    #         }
    #         self.post(url_forgot_password, data=payload)
    #         forgot_mail = mail.outbox.pop()
    #         token = get_forgot_password_token(forgot_mail.body)
    #         payload = {
    #             "password": "123123123",
    #             "confirm_password": "123123123",
    #             "token": token
    #         }
    #         self.post(url_reset_password, data=payload, status_code=status.HTTP_400_BAD_REQUEST)
