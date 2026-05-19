from django.utils.dateparse import parse_date
from rest_framework.pagination import PageNumberPagination


class WalletHistoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def apply_date_filter(qs, request):
    start = request.query_params.get("start_date")
    end = request.query_params.get("end_date")

    if start:
        qs = qs.filter(created_at__date__gte=parse_date(start))
    if end:
        qs = qs.filter(created_at__date__lte=parse_date(end))

    return qs
