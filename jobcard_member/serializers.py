from rest_framework import serializers
from .models import MbrDocuments
from jobcard_business.models import JobApplication, Job

class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
        read_only_fields = ["card_number"]


class JobApplicationCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    resume = serializers.CharField(max_length=255)
    institute_id= serializers.CharField(max_length=6)
    cover_letter = serializers.CharField(allow_blank=True, required=False)
       
       
class JobApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job_id = serializers.IntegerField(source='job.id', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job_id', 'job_title', 'company_name', 'resume', 'cover_letter', 'status', 'applied_at']
