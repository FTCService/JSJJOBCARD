# serializers.py
from rest_framework import serializers
from jobcard_staff.models import JobApplication, Job

class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['member_id', 'candidate_name']
        
class JobPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'location', 'workplace',
            'application_end_date', 'job_type', 'min_salary', 'max_salary',
            'requirements', 'about_company', 'description',
            'languages', 'area_of_work', 'industry', 'number_of_posts',
            'education_levels', 'specialisations', 'key_skills',
            'image', 'video', 'created_at'
        ]
