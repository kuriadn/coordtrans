from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('users/', include('profiles.urls')),
    path('admin/', admin.site.urls),
    path('coord_trans/', include('coordtrans.urls')),
    path('traverse/', include('traverse.urls')),
    path('area/', include('areacalc.urls')),
    path('bearing/', include('geocalc.urls')),
    path('crs/', include('crstrans.urls')),
    path('', include('accounts.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
