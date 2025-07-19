from rest_framework import serializers
from jobcard_business.models import Job, JobApplication
from .models import Campaign, CampaignAudience, EmailContent, SMSContent, WhatsAppContent, CampaignDeliveryLog, Inquiry

from helpers.utils import get_member_details_by_card
import os
from urllib.parse import urlparse

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
    resume_name = serializers.SerializerMethodField()
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job_id', 'job_title', 'company_name', 'member_card',
            'full_name', 'email','resume','resume_name', 'cover_letter', 'status', 'applied_at',
            
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
    def get_resume_name(self, obj):
        resume_url = obj.resume
        if resume_url and resume_url.strip():
            try:
                path = urlparse(resume_url).path
                full_filename = os.path.basename(path)
                return full_filename[-15:] if len(full_filename) >= 15 else full_filename
            except Exception:
                return None
        return None


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class CampaignAudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignAudience
        fields = [
            'id',
            'campaign',
            'user',
            'added_at',
        ]
        read_only_fields = ['id', 'added_at']
        
        
class EmailContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailContent
        fields = [
            'id',
            'campaign',
            'subject',
            'body',
            'footer',
        ]
        read_only_fields = ['id']
        
class SMSContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSContent
        fields = [
            'id',
            'campaign',
            'message',
        ]
        read_only_fields = ['id']
        
class WhatsAppContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppContent
        fields = [
            'id',
            'campaign',
            'template_name',
            'message_parameters',
        ]
        read_only_fields = ['id']
        
class CampaignDeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignDeliveryLog
        fields = [
            'id',
            'campaign',
            'user',
            'status',
            'sent_at',
            'response_data',
        ]
        read_only_fields = ['id']
        
class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['full_name', 'email', 'phone_number', 'service', 'message']
