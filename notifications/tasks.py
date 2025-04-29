from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_notification_email(email, subject, message):
    context = {
        'subject': subject,
        'message': message,
        'domain': settings.FRONTEND_URL, 
    }

    html_message = render_to_string('email/notification_email.html', context)

    send_mail(
        subject,
        message,  
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )