from rest_framework import serializers
from .models import Document,Job

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        ref_name = 'BusinessDocumentSerializer'  # 👈 THIS FIXES THE CONFLICT

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'