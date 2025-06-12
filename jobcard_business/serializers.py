from rest_framework import serializers
from jobcard_member.models import JobApplication

class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['candidate_name', 'member_id']
        ref_name = "EmployerCandidateSummary"