# -*- coding: utf-8 -*-

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # path('', lambda request: redirect('api:login', permanent=True)),
]
