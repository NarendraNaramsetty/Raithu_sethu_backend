from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import DataGovMandiService


class MandiPriceListView(APIView):
    """
    Returns live mandi market prices powered by official data.gov.in API
    with intelligent fallback to local APMC database.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        state = request.query_params.get('state', '').strip()
        commodity = request.query_params.get('commodity') or request.query_params.get('crop', '').strip()
        district = request.query_params.get('district', '').strip()
        market = request.query_params.get('market') or request.query_params.get('mandi', '').strip()
        search = request.query_params.get('search', '').strip()
        limit = request.query_params.get('limit', 50)
        offset = request.query_params.get('offset', 0)
        force_refresh = request.query_params.get('refresh', '').lower() in ['true', '1', 'yes']

        data = DataGovMandiService.get_live_mandi_prices(
            state=state if state else None,
            commodity=commodity if commodity else None,
            district=district if district else None,
            market=market if market else None,
            search=search if search else None,
            limit=limit,
            offset=offset,
            force_refresh=force_refresh
        )

        return Response(data, status=status.HTTP_200_OK)


class MandiPriceSummaryView(APIView):
    """
    Returns market summary metrics, top gainers, and MSP coverage status.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        state = request.query_params.get('state', '').strip()
        summary = DataGovMandiService.get_mandi_summary(state=state if state else None)
        return Response(summary, status=status.HTTP_200_OK)


class MandiFilterOptionsView(APIView):
    """
    Returns selectable state and commodity filter options for the frontend UI.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        filters = DataGovMandiService.get_filter_options()
        return Response(filters, status=status.HTTP_200_OK)
