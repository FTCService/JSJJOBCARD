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
        fields = [
            'id',
            'job',
            'candidate_name',
            'candidate_email',
            'member_card',
            'location',
            'resume',
            'cover_letter',
            'applied_at',
            'application_number'  # ✅ Required to expose this field
        ]
        read_only_fields = ['applied_at']
        
class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
