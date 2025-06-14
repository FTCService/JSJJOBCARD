from rest_framework import serializers
from .models import MbrDocuments
from jobcard_staff.models import JobApplication

class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
        read_only_fields = ["card_number"]

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['application_number']