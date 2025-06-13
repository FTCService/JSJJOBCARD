from rest_framework import serializers
from .models import Job, JobApplication
from jobcard_member.models import MbrDocuments


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        
class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['applied_at']
        
class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
