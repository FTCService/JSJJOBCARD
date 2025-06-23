from rest_framework import serializers
from jobcard_business.models import Job, JobApplication
from helpers.utils import get_member_details_by_card


class JobpostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        

        
class JobApplicationStaffViewSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job_id = serializers.IntegerField(source='job.id', read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_id', 'job_title', 'company_name', 'member_card',
            'full_name', 'email','resume', 'cover_letter', 'status', 'applied_at',
            
        ]

    def get_full_name(self, obj):
         
        member_card = obj.member_card
        try:
            member_data = get_member_details_by_card(member_card)
            return member_data.get('full_name')
        except Exception:
            return None

    def get_email(self, obj):
          # Replace with actual path
        member_card = obj.member_card
        try:
            member_data = get_member_details_by_card(member_card)
            return member_data.get('email')
        except Exception:
            return None

