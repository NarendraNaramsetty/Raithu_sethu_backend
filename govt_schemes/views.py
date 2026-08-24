import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import GovtScheme
from .serializers import GovtSchemeSerializer
from .fixtures_data import GOVT_SCHEMES_DATA

logger = logging.getLogger(__name__)


def get_or_seed_schemes():
    """Returns database schemes, auto-seeding if the table is empty."""
    try:
        if not GovtScheme.objects.exists():
            schemes_to_create = [
                GovtScheme(
                    title=item["title"],
                    subtitle=item["subtitle"],
                    category=item["category"],
                    benefit_amount=item["benefit_amount"],
                    eligibility=item["eligibility"],
                    required_documents=item["required_documents"],
                    application_status=item["application_status"],
                    official_portal_url=item["official_portal_url"],
                )
                for item in GOVT_SCHEMES_DATA
            ]
            GovtScheme.objects.bulk_create(schemes_to_create)
            logger.info("Successfully seeded %d government schemes to database.", len(schemes_to_create))
        return GovtScheme.objects.all()
    except Exception as e:
        logger.warning("Database scheme query or seed failed: %s. Using in-memory dataset.", e)
        return None


class GovtSchemeListView(APIView):
    """
    Returns up-to-date central and state agricultural support schemes,
    subsidies, eligibility requirements, and portal application links.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        category = request.query_params.get('category', '').strip()
        search = request.query_params.get('search', '').strip().lower()

        db_schemes = get_or_seed_schemes()

        if db_schemes is not None:
            schemes = db_schemes
            if category and category.lower() != 'all':
                schemes = schemes.filter(category__icontains=category)
            if search:
                schemes = schemes.filter(title__icontains=search) | schemes.filter(subtitle__icontains=search)
            return Response(GovtSchemeSerializer(schemes, many=True).data, status=status.HTTP_200_OK)

        # Fallback to in-memory curated data
        results = []
        for idx, item in enumerate(GOVT_SCHEMES_DATA, start=1):
            if category and category.lower() != 'all' and category.lower() not in item['category'].lower():
                continue
            if search and (search not in item['title'].lower() and search not in item['subtitle'].lower()):
                continue
            results.append({
                "id": idx,
                "title": item["title"],
                "subtitle": item["subtitle"],
                "tag": item["category"],
                "benefit": item["benefit_amount"],
                "eligibility": item["eligibility"],
                "documents": item["required_documents"],
                "status": item["application_status"],
                "link": item["official_portal_url"],
            })

        return Response(results, status=status.HTTP_200_OK)


class GovtSchemeDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            scheme = GovtScheme.objects.get(pk=pk)
            return Response(GovtSchemeSerializer(scheme).data, status=status.HTTP_200_OK)
        except GovtScheme.DoesNotExist:
            try:
                pk_int = int(pk)
                if 1 <= pk_int <= len(GOVT_SCHEMES_DATA):
                    item = GOVT_SCHEMES_DATA[pk_int - 1]
                    return Response({
                        "id": pk_int,
                        "title": item["title"],
                        "subtitle": item["subtitle"],
                        "tag": item["category"],
                        "benefit": item["benefit_amount"],
                        "eligibility": item["eligibility"],
                        "documents": item["required_documents"],
                        "status": item["application_status"],
                        "link": item["official_portal_url"],
                    }, status=status.HTTP_200_OK)
            except (ValueError, IndexError):
                pass
            return Response({"detail": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)
