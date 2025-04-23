from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_verification_email(email, token, uid, first_name):
    context = {
        'user': {'first_name': first_name},
        'uid': uid,
        'token': token,
        'domain': settings.FRONTEND_URL
    }

    message = render_to_string('email/verification_email.html', context)

    send_mail(
        'Email Verification',
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=message,
        fail_silently=False,
    )


@shared_task
def send_password_reset_email(email, uid, token, first_name):
    context = {
        'user': {'first_name': first_name},
        'uid': uid,
        'token': token,
        'domain': settings.FRONTEND_URL
    }

    message = render_to_string('email/password_reset_email.html', context)

    send_mail(
        'Reset Your Password',
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=message,
        fail_silently=False,
    )