from django.urls import path

from . import views

app_name = 'traverse'

urlpatterns = [
    path('', views.adjust_traverse, name='adjust'),
]
