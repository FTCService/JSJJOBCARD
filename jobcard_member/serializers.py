from rest_framework import serializers
from .models import MbrDocuments
from jobcard_business.models import JobApplication, Job, Feedback
from helpers.utils import get_member_details_by_card
class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MbrDocuments
        fields = '__all__'
        read_only_fields = ["card_number"]


class JobApplicationCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    resume = serializers.CharField(max_length=255, allow_blank=True, required=False)
    institute_id = serializers.CharField(max_length=6, allow_blank=True, required=False)
    cover_letter = serializers.CharField(allow_blank=True, required=False)

class JobApplicationListSerializer(serializers.ModelSerializer):
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






class DocumentShareSerializer(serializers.Serializer):
    selected_fields = serializers.ListField(child=serializers.CharField())
    pin = serializers.CharField()
    access_time_minutes = serializers.IntegerField()
    
    
    


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'card_number',
            'business_id',
            'happiness_rating',
            'has_issues',
            'issues_detail',
            'liked_most',
            'suggestions'
            
        ]
        extra_kwargs = {
            'card_number': {'required': False},
            'business_id': {'required': False},
        }