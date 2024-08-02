# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Изменено с 'user_set' на 'custom_user_set'
        blank=True,
        help_text='Группы, к которым принадлежит этот пользователь. Пользователь получит все привелегии, предоставленные каждой из его групп.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Изменено с 'user_set' на 'custom_user_set'
        blank=True,
        help_text='Привелегии для данного пользователя.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.email


class Bike(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_RENTED = 'rented'
    STATUS_UNDER_REPAIR = 'under_repair'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Доступен'),
        (STATUS_RENTED, 'Арендован'),
        (STATUS_UNDER_REPAIR, 'В ремонте'),
    ]

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Велосипед"
        verbose_name_plural = "Велосипеды"


class Rental(models.Model):
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.bike.name} - {self.user.username}'

    def calculate_cost(self):
        if self.end_time:
            duration = self.end_time - self.start_time
            return (duration.total_seconds() / 3600) * self.bike.rental_price
        return None
