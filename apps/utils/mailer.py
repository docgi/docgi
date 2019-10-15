from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings as app_settings


def send_mail(subject: str, email: str, text_template: str, html_template: str, context: dict):
    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)
    email = EmailMultiAlternatives(subject, text_content, app_settings.ADMIN_EMAIL, [email])
    email.attach_alternative(html_content, "text/html")
    email.send()
