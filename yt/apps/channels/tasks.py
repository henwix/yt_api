import os

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def simple_task():
    subject = "Thanks for signing up on our platform!"
    message = "This is simple notification that"
    from_email = os.environ.get("EMAIL_HOST_USER")
    recipient_list = ["492b675xhpd1@gmail.com"]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return "Email sent to user."
