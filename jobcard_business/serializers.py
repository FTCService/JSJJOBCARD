# serializers.py
from rest_framework import serializers
from . import models

 
class InstitutionJobListSerializer(serializers.ModelSerializer):  # Renamed class
    class Meta:
        model = models.Job
        fields = '__all__'


