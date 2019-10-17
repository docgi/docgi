from os import path

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings as app_settings

from apps.utils.mailer import send_mail
from . import models

URL_FRONT_END_JOIN_INVITE = "join-invite"


@receiver(post_save, sender=models.Invitation)
def send_invitation(sender, instance: models.Invitation, created):
    link_join = path.join(*[app_settings.FRONT_END_HOST_NAME,
                            URL_FRONT_END_JOIN_INVITE,
                            instance.uuid])
    ctx = dict(
        inviter=instance.inviter.username,
        link_join=link_join,
        email=instance.email,
        workspace=instance.workspace
    )
    send_mail(subject="Invitation",
              email=instance.email,
              html_template="email/invitation/invitation.html",
              text_template="email/invitation/invitation.txt",
              context=ctx)
