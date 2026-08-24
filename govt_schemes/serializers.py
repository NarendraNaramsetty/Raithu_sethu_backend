from rest_framework import serializers
from .models import GovtScheme

class GovtSchemeSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(source='category')
    benefit = serializers.CharField(source='benefit_amount')
    status = serializers.CharField(source='application_status')
    documents = serializers.ListField(source='required_documents')
    link = serializers.URLField(source='official_portal_url')

    class Meta:
        model = GovtScheme
        fields = [
            'id', 'title', 'subtitle', 'tag', 'benefit',
            'eligibility', 'documents', 'status', 'link', 'created_at'
        ]
