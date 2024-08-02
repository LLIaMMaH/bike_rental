# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('available/', views.AvailableBikesView.as_view(), name='available'),
    path('rent/<int:bike_id>/', views.RentBikeView.as_view(), name='rent'),
    path('return/<int:rental_id>/', views.ReturnBikeView.as_view(), name='return'),
    path('bikes/<int:bike_id>/status/', views.UpdateBikeStatusView.as_view(), name='update_bike_status'),
]
