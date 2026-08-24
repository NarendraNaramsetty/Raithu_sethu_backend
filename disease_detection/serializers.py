from rest_framework import serializers
from .models import CropDiseaseKnowledge, LeafScanHistory

class CropDiseaseKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropDiseaseKnowledge
        fields = '__all__'

class LeafScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeafScanHistory
        fields = '__all__'
