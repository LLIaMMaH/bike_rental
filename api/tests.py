# -*- coding: utf-8 -*-

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser


@pytest.mark.django_db
def test_user_registration(client):
    url = reverse('register')
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email='testuser@example.com').exists()


@pytest.mark.django_db
def test_user_login(client):
    user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword123')
    url = reverse('login')
    data = {
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data