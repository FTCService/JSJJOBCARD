from rest_framework import serializers
from jobcard_business.models import Job



class JobpostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        

        
class JobMitraApplySerializer(serializers.Serializer):
    member_card = serializers.IntegerField(help_text="JSJ Member Card Number")