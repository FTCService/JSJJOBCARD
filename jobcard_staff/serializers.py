from rest_framework import serializers
from jobcard_business.models import Job



class JobpostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        

        
class JobMitraApplySerializer(serializers.Serializer):
    member_card = serializers.IntegerField(help_text="JSJ Member Card Number")
    resume = serializers.CharField(help_text="Resume text or file path")
    cover_letter = serializers.CharField(required=False, allow_blank=True)