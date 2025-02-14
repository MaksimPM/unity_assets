import random
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from users.models import User


@shared_task
def send_confirmation_email(user_id):
    user = User.objects.get(id=user_id)
    confirmation_code = str(random.randint(100000, 999999))

    user.confirmation_code = confirmation_code
    user.confirmation_code_created_at = timezone.now()
    user.save()

    subject = 'Добро пожаловать!'
    message = f'Ваш код для подтверждения почты:\n {confirmation_code}'
    to_email = [user.email]
    from_email = settings.EMAIL_HOST_USER

    sent_count = send_mail(subject, message, from_email, to_email, fail_silently=False)
    if sent_count == 0:
        print(f"Ошибка отправки письма на {user.email}")


@shared_task
def send_password_reset_email(user_id):
    user = User.objects.get(id=user_id)
    print(f'Письмо для сброса пароля отправлено - {user.email}')

    subject = 'Cброс пароля'
    message = f'Перейдите по ссылке для сброса пароля: http://localhost:8000/users/recovery/{user.password}/'
    to_email = [user.email]
    from_email = settings.EMAIL_HOST_USER

    sent_count = send_mail(subject, message, from_email, to_email, fail_silently=False)
    if sent_count == 0:
        print(f"Ошибка отправки письма на {user.email}")
