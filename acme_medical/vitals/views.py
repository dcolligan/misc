from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from vitals.models import Patient
from vitals.models import Vital
from vitals.models import Measurement
from vitals.models import PageData
from vitals.serializers import PatientSerializer
from vitals.serializers import VitalSerializer
from vitals.serializers import MeasurementSerializer
from vitals.serializers import MeasurementSerializerLessFields
from vitals.serializers import PageSerializer
import itertools


def home(request):
   return render(request, 'vitals/home.html')


class PatientList(generics.ListCreateAPIView):
   queryset = Patient.objects.all()
   serializer_class = PatientSerializer


class PatientDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = Patient.objects.all()
   serializer_class = PatientSerializer


class VitalList(generics.ListAPIView):
   queryset = Vital.objects.all()
   serializer_class = VitalSerializer


class VitalDetail(generics.RetrieveAPIView):
   queryset = Vital.objects.all()
   serializer_class = VitalSerializer


class MeasurementList(generics.ListCreateAPIView):
   queryset = Measurement.objects.all()
   serializer_class = MeasurementSerializer

   def post(self, request, *args, **kwargs):
      """
      Overridden to use a different serializer
      """
      serializer = MeasurementSerializerLessFields(data=request.DATA)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   

class MeasurementDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = Measurement.objects.all()
   serializer_class = MeasurementSerializer


class PagePatientDetail(APIView):

   def get(self, request, *args, **kwargs):
      limit = 10
      if 'limit' in request.GET:
         limit = request.GET['limit']
      patient_id = kwargs['patient_id']
      patient = Patient.objects.get(pk=patient_id)
      vitals = Vital.objects.all()
      results = []
      for vital in vitals:
         vital_id = vital.id
         measurements = Measurement.objects.filter(patient_id=patient_id, vital_id=vital_id).order_by('-date')[:limit]
         results.append(measurements)
      flat_results = itertools.chain(*results)
      page_data = PageData(patient, None, vitals, flat_results)
      serializer = PageSerializer(page_data)
      return Response(serializer.data)


class PageVitalDetail(APIView):

   def get(self, request, *args, **kwargs):
      limit = 10
      if 'limit' in request.GET:
         limit = request.GET['limit']
      vital_slug = kwargs['vital_slug']
      patient_id = kwargs['patient_id']
      vital = Vital.objects.get(slug=vital_slug)
      vital_id = vital.id
      vitals = Vital.objects.all()
      patient = Patient.objects.get(pk=patient_id)
      measurements = Measurement.objects.filter(patient_id=patient_id, vital_id=vital_id).order_by('-date')[:limit]
      page_data = PageData(patient, vital, vitals, measurements)
      serializer = PageSerializer(page_data)
      return Response(serializer.data)
      
