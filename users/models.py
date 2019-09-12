from django.db import models, IntegrityError
from model_utils.models import SoftDeletableModel
from django.contrib.auth.models import AbstractUser

from utils import strings


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @classmethod
    def get_or_create(cls, email: str):
        try:
            user = cls.objects.get(email__iexact=email)
        except cls.DoesNotExist:
            while True:
                try:
                    temp_username = strings.gen_username(email=email)
                    user = cls(email=email.lower(), username=temp_username)
                    user.set_unusable_password()
                    user.save()
                except IntegrityError:
                    continue
                else:
                    break
        return user

    def __str__(self):
        return self.username or self.email
