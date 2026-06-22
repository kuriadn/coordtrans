from django.urls import path

from . import views

app_name = 'geocalc'

urlpatterns = [
    path('', views.compute_bearing_distance, name='compute'),
]
