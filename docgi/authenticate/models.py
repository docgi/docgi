from django.db import models
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel

User = get_user_model()


class ResetPasswordToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    is_active = models.BooleanField(default=True)
    token = models.TextField()

    def __str__(self):
        return f"User ${self.user_id}"
