from rest_framework import serializers
from .models import MbrDocuments, JobPost, JobApplication

class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
        read_only_fields = ["card_number"]

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'
        
class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        ref_name = "MemberJobApplication"