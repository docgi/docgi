from os import path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import get_storage_class
from django.db import models, IntegrityError
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from apps.utils import strings

storage = get_storage_class()()


class User(AbstractUser):
    def avatar_path(self, filename, *args, **kwargs):
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
        email = email.lower()
        try:
            user = cls.objects.get(email__iexact=email)
        except cls.DoesNotExist:
            username = strings.gen_username(email=email)

            while cls.objects.filter(username__iexact=username).exists():
                username = strings.gen_username(email=email)

            user = cls.objects.create(
                email=email, username=username
            )
            user.set_unusable_password()
        return user

    def __str__(self):
        return self.username or self.email
