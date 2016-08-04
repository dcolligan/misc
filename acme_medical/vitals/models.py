from django.db import models
from django.utils import timezone

### Database Objects ###

class Patient(models.Model):
   name = models.TextField()

   def __str__(self):
      return self.name


class Vital(models.Model):
   name = models.TextField()
   slug = models.TextField()
   unitLabel = models.TextField()
   unitLabelShort = models.TextField()
   unitCount = models.IntegerField()

   def __str__(self):
      return self.name


class Measurement(models.Model):
   vital = models.ForeignKey(Vital)
   patient = models.ForeignKey(Patient)
   value1 = models.DecimalField(max_digits=10, decimal_places=5)
   value2 = models.DecimalField(max_digits=10, decimal_places=5)
   date = models.DateTimeField()

   def clean_fields(self, exclude=None):
      """
      Ignore date when validating
      """
      return super(Measurement, self).clean_fields(exclude=['date'])

   def save(self, *args, **kwargs):
      """
      Set date to current time before DB write if not specified
      """
      if not self.date:
         self.date = timezone.now()
      return super(Measurement, self).save(*args, **kwargs)

   def __str__(self):
      if self.value2:
         return '%s/%s %s' % (self.value1, self.value2, self.vital.unitLabelShort)
      else:
         return '%s %s' % (self.value1, self.vital.unitLabelShort)

### Serialization Objects ###

class PageData(object): 

   def __init__(self, patient, vital, vitals, measurements):
      self.patient = patient
      self.vital = vital
      self.vitals = vitals
      self.measurements = measurements
