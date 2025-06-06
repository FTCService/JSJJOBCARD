from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    tenth_certificate = serializers.FileField(required=False)
    pan_card = serializers.FileField(required=False)
    resume = serializers.FileField(required=False)
    # ... add other fields if you want

    class Meta:
        model = Document
        fields = '__all__'

