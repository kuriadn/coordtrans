from django.contrib import admin
from .models import *

class TransRequestAdmin(admin.ModelAdmin):
  fields = ('user', 'sheet', 'inpoints', 'points', 'trtype', 'datedone',)
  list_display = ('user', 'sheet', 'inpoints', 'points', 'trtype', 'datedone',)
  list_filter = ('user', 'sheet', 'inpoints', 'points', 'trtype', 'datedone',)
  list_per_page = 10

class SheetReferenceAdmin(admin.ModelAdmin):
  fields = ('shtno', 'pt1', 'pt2', 'pt3', 'pt4', 'scan')
  list_display = ('shtno', 'pt1', 'pt2', 'pt3', 'pt4','scan',)
  list_filter = ('shtno', 'pt1', 'pt2', 'pt3', 'pt4',)
  list_per_page = 10

class ControlPointAdmin(admin.ModelAdmin):
  fields = ('pid', 'geog_x', 'geog_y', 'cass_x', 'cass_y', 'utm_x', 'utm_y',)
  list_display = ('pid', 'geog_x', 'geog_y', 'cass_x', 'cass_y', 'utm_x', 'utm_y',)
  list_filter = ('pid', 'geog_x', 'geog_y', 'cass_x', 'cass_y', 'utm_x', 'utm_y',)
  list_per_page = 10

admin.site.register(TransRequest, TransRequestAdmin)
admin.site.register(SheetReference, SheetReferenceAdmin)
admin.site.register(ControlPoint, ControlPointAdmin)