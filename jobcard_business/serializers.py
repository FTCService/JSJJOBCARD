# serializers.py
from rest_framework import serializers
from . import models
from helpers.utils import get_member_details_by_card

 
class InstitutionJobListSerializer(serializers.ModelSerializer):  # Renamed class
    class Meta:
        model = models.Job
        fields = '__all__'


class JobApplicationListForBusinessSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    full_name = serializers.SerializerMethodField()
   

    class Meta:
        model = models.JobApplication
        fields = [
            'id', 'job_title', 'member_card',
            'full_name','status', 'applied_at',
            
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
        
