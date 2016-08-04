from rest_framework import serializers
from vitals.models import Patient
from vitals.models import Vital
from vitals.models import Measurement


class PatientSerializer(serializers.ModelSerializer):
   class Meta:
      model = Patient
      fields = ('id', 'name')


class VitalSerializer(serializers.ModelSerializer):
   class Meta:
      model = Vital
      fields = ('id', 'name', 'slug', 'unitLabel', 'unitLabelShort', 'unitCount')


class MeasurementSerializer(serializers.ModelSerializer):
   class Meta:
      model = Measurement
      fields = ('id', 'vital', 'patient', 'value1', 'value2', 'date')

class MeasurementSerializerLessFields(serializers.ModelSerializer):
   """
   Same as MeasurementSerializer with a subset of fields that leaves out
   what we don't want to validate.
   """
   class Meta:
      model = Measurement
      fields = ('id', 'vital', 'patient', 'value1', 'value2')


class PageSerializer(serializers.Serializer):
   patient = PatientSerializer()
   vital = VitalSerializer()
   vitals = VitalSerializer(many=True)
   measurements = MeasurementSerializer(many=True)
