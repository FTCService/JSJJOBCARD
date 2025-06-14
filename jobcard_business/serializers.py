# serializers.py
from rest_framework import serializers
from jobcard_staff.models import JobApplication, Job

class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['member_card', 'candidate_name']
        
class InstitutionJobSerializer(serializers.ModelSerializer):  # Renamed class
    class Meta:
        model = Job
        fields = '__all__'

class JobApplicationCountSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source='id')
    total_applicants = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['job_id', 'title', 'company_name', 'location', 'total_applicants']

    def get_total_applicants(self, obj):
        return obj.applications.count()  # ✅ Uses related_name from your model