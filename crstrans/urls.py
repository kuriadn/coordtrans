from django.urls import path

from . import views

app_name = 'crstrans'

urlpatterns = [
    path('', views.transform_points_view, name='transform'),
    path('upload/', views.transform_file_view, name='upload'),
]
