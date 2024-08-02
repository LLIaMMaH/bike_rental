# -*- coding: utf-8 -*-

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from bike_rental import settings
from .models import Rental


@shared_task
def send_rental_notification(rental_id):
    try:
        rental = Rental.objects.get(id=rental_id)
        context = {
            'rental': rental,
            'action': 'арендовали',
        }
        subject = 'Уведомление об аренде велосипеда'
        message = render_to_string('api/rental_notification_email.html', context)
        send_mail(subject, message, 'from@example.com', [rental.user.email], fail_silently=False)
    except Rental.DoesNotExist:
        error_message = f'Ошибка при отправке уведомления о аренде велосипеда с ID {rental_id}. Объект не найден.'
        send_mail('Ошибка аренды велосипеда', error_message, 'api@bike-rent.ru', settings.ADMINS, fail_silently=False)
    except Exception as e:
        # Обработка других ошибок отправки письма
        error_message = f'Произошла ошибка при отправке уведомления о аренде велосипеда с ID {rental_id}: {str(e)}'
        send_mail('Ошибка отправки уведомления', error_message, 'api@bike-rent.ru', settings.ADMINS,
                  fail_silently=False)


@shared_task
def send_return_notification(rental_id):
    try:
        rental = Rental.objects.get(id=rental_id)
        context = {
            'rental': rental,
            'action': 'вернули',
        }
        subject = 'Уведомление об возврате велосипеда'
        message = render_to_string('api/return_notification_email.html', context)
        send_mail(subject, message, 'from@example.com', [rental.user.email], fail_silently=False)
    except Rental.DoesNotExist:
        error_message = f'Ошибка при отправке уведомления о возврате велосипеда с ID {rental_id}. Объект не найден.'
        send_mail('Ошибка возврата велосипеда', error_message, 'api@bike-rent.ru', settings.ADMINS, fail_silently=False)
    except Exception as e:
        # Обработка других ошибок отправки письма
        error_message = f'Произошла ошибка при отправке уведомления о возврате велосипеда с ID {rental_id}: {str(e)}'
        send_mail('Ошибка возврата уведомления', error_message, 'api@bike-rent.ru', settings.ADMINS,
                  fail_silently=False)
