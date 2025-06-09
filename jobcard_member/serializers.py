from rest_framework import serializers
from . import models

class MbrDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MbrDocuments
        fields = '__all__'
        read_only_fields = ["card_number"]