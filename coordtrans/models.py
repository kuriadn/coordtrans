from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone 

def upload_handler(instance, other):
  return 'sheets/' + other

class ControlPoint(models.Model):
  pid = models.CharField(max_length=8, primary_key=True, verbose_name='Point ID.')
  geog_x = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='Geographic - E')
  geog_y = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='Geographic - N')
  cass_x = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='Cassini - E')
  cass_y = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='Cassini - N')
  utm_x = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='U.T.M. - E')
  utm_y = models.DecimalField(max_digits=12, decimal_places=3, verbose_name='U.T.M. - N')

  def __str__(self):
  	return self.pid

class SheetReference(models.Model):
  shtno = models.CharField(max_length=8, primary_key=True, verbose_name='Sheet No.')
  pt1 = models.ForeignKey(ControlPoint, on_delete=models.CASCADE, 
  		related_name='control_pt1', verbose_name='Point 1')
  pt2 = models.ForeignKey(ControlPoint, on_delete=models.CASCADE,  
  		related_name='control_pt2', verbose_name='Point 2')
  pt3 = models.ForeignKey(ControlPoint, on_delete=models.CASCADE,  
  		related_name='control_pt3', verbose_name='Point 3')
  pt4 = models.ForeignKey(ControlPoint, on_delete=models.CASCADE,  
  		related_name='control_pt4', verbose_name='Point 4')
  scan = models.ImageField('Sheet Image', upload_to='sheets/')

  def __str__(self):
  	return self.shtno

  class Meta:
  	ordering = ['shtno']

class TransRequest(models.Model):
  TYPES = (('cassini','Cassini'), ('utm','U.T.M.'),)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  sheet = models.ForeignKey(SheetReference, on_delete=models.CASCADE)
  inpoints = models.IntegerField(verbose_name='Points Given', default=-1)
  points = models.IntegerField(verbose_name='Points Transformed')
  trtype = models.CharField(max_length=8, choices=TYPES, verbose_name='Transformation Type')
  datedone = models.DateField(default=timezone.now, verbose_name='Date Done')

  def __str__(self):
  	return '{0} - {1}'.format(self.user.name, str(self.datedone))

  class Meta:
  	verbose_name='Transformation Request'