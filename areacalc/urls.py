from django.urls import path

from . import views

app_name = 'areacalc'

urlpatterns = [
    path('', views.compute_parcel, name='compute'),
]
