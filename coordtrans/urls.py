from django.urls import path

from . import views

app_name = 'coords'

urlpatterns = [
    path('controlpoints/', views.controlpoint_list, name='controlpoint_list'),
    path('controlpoints/create/', views.controlpoint_create, name='controlpoint_create'),
    path('controlpoints/<str:pk>/update/', views.controlpoint_update, name='controlpoint_update'),
    path('controlpoints/<str:pk>/delete/', views.controlpoint_delete, name='controlpoint_delete'),

    path('sheets/', views.sheetreference_list, name='sheetreference_list'),
    path('sheets/create/', views.sheetreference_create, name='sheetreference_create'),
    path('sheets/<path:pk>/update/', views.sheetreference_update, name='sheetreference_update'),
    path('sheets/<path:pk>/delete/', views.sheetreference_delete, name='sheetreference_delete'),

    path('transformations/', views.transrequest_list, name='transrequest_list'),
    path('transformations/create/', views.transrequest_create, name='transrequest_create'),
    path('transformations/<int:pk>/update/', views.transrequest_update, name='transrequest_update'),
    path('transformations/<int:pk>/delete/', views.transrequest_delete, name='transrequest_delete'),

    path('getfile/', views.upload_file, name='getfile'),
    path('enter_points/', views.enter_points, name='enterpoints'),
]
