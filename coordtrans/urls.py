from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^controlpoints/$', views.controlpoint_list, name='controlpoint_list'),
   url(r'^controlpoints/create/$', views.controlpoint_create, name='controlpoint_create'),
   url(r'^controlpoints/(?P<pk>\w+)/update/$', views.controlpoint_update, name='controlpoint_update'),
   url(r'^controlpoints/(?P<pk>\w+)/delete/$', views.controlpoint_delete, name='controlpoint_delete'),
 
   url(r'^sheets/$', views.sheetreference_list, name='sheetreference_list'),
   url(r'^sheets/create/$', views.sheetreference_create, name='sheetreference_create'),
   url(r'^sheets/(?P<pk>\d+/\d{1})/update/$', views.sheetreference_update, name='sheetreference_update'),
   url(r'^sheets/(?P<pk>\d+/\d{1})/delete/$', views.sheetreference_delete, name='sheetreference_delete'),

   url(r'^transformations/$', views.transrequest_list, name='transrequest_list'),
   url(r'^transformations/create/$', views.transrequest_create, name='transrequest_create'),
   url(r'^transformations/(?P<pk>\d+)/update/$', views.transrequest_update, name='transrequest_update'),
   url(r'^transformations/(?P<pk>\d+)/delete/$', views.transrequest_delete, name='transrequest_delete'),

   url(r'^getfile/$', views.upload_file, name="getfile"),
   url(r'^enter_points/$', views.enter_points, name="enterpoints"),
 
 ]