import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from .models import CropDiseaseKnowledge, LeafScanHistory
from .serializers import CropDiseaseKnowledgeSerializer, LeafScanHistorySerializer
from .services import ClaudeDiseaseService, INDIAN_AGRONOMY_FALLBACK_DB


class AnalyzeLeafView(APIView):
    """
    Analyzes crop leaf photos with Anthropic Claude Vision AI and provides
    crop-validated pathology, severity, organic remedies, chemical treatments, and prevention tips.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uploaded_image = request.FILES.get('image', None)
        language = request.data.get('language', 'en')

        # Extract authenticated user if token is provided
        user = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            key = auth_header.split(' ')[1]
            token_obj = Token.objects.filter(key=key).first()
            if token_obj:
                user = token_obj.user
        elif request.user and request.user.is_authenticated:
            user = request.user

        # Run Claude Vision + Validation + Fallback Engine
        analysis = ClaudeDiseaseService.analyze_crop_leaf(
            image_file=uploaded_image,
            language=language
        )

        status_val = analysis.get("status", "success")

        # If invalid or blurry image, return early without saving corrupted scan
        if status_val in ["invalid_image", "insufficient_image"]:
            return Response(analysis, status=status.HTTP_200_OK)

        crop_data = analysis.get("crop", {})
        disease_data = analysis.get("disease", {})
        confidence_data = analysis.get("confidence", {})
        severity_data = analysis.get("severity", {})

        crop_name = crop_data.get("name", "Unknown Crop") if isinstance(crop_data, dict) else str(crop_data)
        crop_sci = crop_data.get("scientific_name", "") if isinstance(crop_data, dict) else ""
        disease_name = disease_data.get("name", "Undetermined") if isinstance(disease_data, dict) else str(disease_data)
        disease_sci = disease_data.get("scientific_name", "") if isinstance(disease_data, dict) else ""
        category = disease_data.get("category", "Foliar Pathology") if isinstance(disease_data, dict) else "Foliar Pathology"

        confidence_level = confidence_data.get("level", "medium") if isinstance(confidence_data, dict) else "medium"
        severity_level = severity_data.get("level", "moderate") if isinstance(severity_data, dict) else "moderate"

        organic_recs = analysis.get("organic_remedy", {}).get("recommendations", [])
        chemical_recs = analysis.get("chemical_treatment", {}).get("recommendations", [])
        prevention_recs = analysis.get("prevention", [])
        symptoms_list = analysis.get("symptoms", [])

        # Save to database
        scan = LeafScanHistory.objects.create(
            user=user,
            image=uploaded_image,
            crop_detected=crop_name,
            crop_scientific_name=crop_sci,
            disease_detected=disease_name,
            disease_scientific_name=disease_sci,
            category=category,
            confidence_level=confidence_level,
            confidence=95.0,
            severity=severity_level.title(),
            source=analysis.get("source", "claude_vision"),
            status=status_val,
            symptoms=json.dumps(symptoms_list) if isinstance(symptoms_list, list) else str(symptoms_list),
            diagnosis_summary=analysis.get("diagnosis_summary", ""),
            organic_solution="\n".join(organic_recs) if isinstance(organic_recs, list) else str(organic_recs),
            chemical_solution="\n".join(chemical_recs) if isinstance(chemical_recs, list) else str(chemical_recs),
            prevention_advice="\n".join(prevention_recs) if isinstance(prevention_recs, list) else str(prevention_recs),
            warning=analysis.get("warning", "")
        )

        response_payload = {
            "id": scan.id,
            "status": status_val,
            "source": analysis.get("source", "claude_vision"),
            "crop": crop_data,
            "disease": disease_data,
            "confidence": confidence_data,
            "severity": severity_data,
            "symptoms": symptoms_list,
            "diagnosis_summary": analysis.get("diagnosis_summary", ""),
            "organic_remedy": analysis.get("organic_remedy", {"recommendations": organic_recs}),
            "chemical_treatment": analysis.get("chemical_treatment", {"recommendations": chemical_recs}),
            "prevention": prevention_recs,
            "warning": analysis.get("warning", ""),
            "message": analysis.get("message", "")
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class ScanHistoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            key = auth_header.split(' ')[1]
            token_obj = Token.objects.filter(key=key).first()
            if token_obj:
                user = token_obj.user
        elif request.user and request.user.is_authenticated:
            user = request.user

        if user:
            scans = LeafScanHistory.objects.filter(user=user).order_by('-created_at')[:10]
            if not scans.exists():
                scans = LeafScanHistory.objects.all().order_by('-created_at')[:10]
        else:
            scans = LeafScanHistory.objects.all().order_by('-created_at')[:10]

        return Response(LeafScanHistorySerializer(scans, many=True).data, status=status.HTTP_200_OK)


class DiseaseKnowledgeListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        items = CropDiseaseKnowledge.objects.all()
        if not items.exists():
            # Seed knowledge base from agronomy database
            created_items = []
            for crop_key, crop_val in INDIAN_AGRONOMY_FALLBACK_DB.items():
                for d_key, d_val in crop_val.get("diseases", {}).items():
                    created_items.append(CropDiseaseKnowledge(
                        crop_name=crop_val["crop_name"],
                        crop_name_native=crop_val.get("crop_telugu", ""),
                        disease_name=d_val["name"],
                        scientific_name=d_val.get("scientific_name", ""),
                        severity=d_val.get("severity", "Moderate"),
                        confidence_default=95.0,
                        symptoms="\n".join(d_val.get("symptoms", [])),
                        organic_solution=d_val.get("organic_solution", ""),
                        chemical_solution=d_val.get("chemical_treatment", ""),
                        prevention_advice=d_val.get("prevention", ""),
                    ))
            if created_items:
                CropDiseaseKnowledge.objects.bulk_create(created_items)
                items = CropDiseaseKnowledge.objects.all()

        return Response(CropDiseaseKnowledgeSerializer(items, many=True).data, status=status.HTTP_200_OK)
