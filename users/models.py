from os import path

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.db import models, IntegrityError
from model_utils.models import SoftDeletableModel
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from utils import strings

storage = get_storage_class()()


class User(SoftDeletableModel, AbstractUser):
    def avatar_path(self, filename, *args, **kwargs):
        """
        Only work for update.
        """
        paths = [
            settings.USER_AVATARS,
            str(self.pk),
            path.basename(filename)
        ]
        return path.join(*paths)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    avatar = models.ImageField(upload_to=avatar_path,
                               storage=storage,
                               blank=True,
                               max_length=256)
    avatar_thumbnail = ProcessedImageField(upload_to=avatar_path,
                                           storage=storage,
                                           processors=[ResizeToFill(
                                               width=settings.AVATAR_THUMBNAIL_WIDTH,
                                               height=settings.AVATAR_THUMBNAIL_HEIGHT
                                           )],
                                           format="JPEG",
                                           options={"quality": 90},
                                           blank=True)

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
