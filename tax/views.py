from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TdsEntry, TdsReport, SalesTds, PurchaseGstEntry, PurchaseGstReport, SalesGstEntry, SalesGstReport
from .serializers import TdsEntrySerializer, TdsReportSerializer, SalesTdsSerializer, PurchaseGstEntrySerializer, PurchaseGstReportSerializer, SalesGstEntrySerializer, SalesGstReportSerializer
from rest_framework.pagination import PageNumberPagination
from buildiq.utils import UtilFunctions


class TdsEntryViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        tds_entry_key = kwargs.get('pk')

        if tds_entry_key:
            return self.retrieve_tds_entry(tds_entry_key)

        return self.list_tds_entries(request)

    def retrieve_tds_entry(self, tds_entry_key):
        try:
            tds_entry = TdsEntry.objects.get(key=tds_entry_key)
            serializer = TdsEntrySerializer(tds_entry)
            return Response(serializer.data)
        except TdsEntry.DoesNotExist:
            return Response({'error': 'TDS entry not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_tds_entries(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = TdsEntry.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No TDS entries found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = TdsEntrySerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = TdsEntrySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class TdsReportViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        tds_report_key = kwargs.get('pk')

        if tds_report_key:
            return self.retrieve_tds_report(tds_report_key)

        return self.list_tds_reports(request)

    def retrieve_tds_report(self, tds_report_key):
        try:
            tds_report = TdsReport.objects.get(key=tds_report_key)
            serializer = TdsReportSerializer(tds_report)
            return Response(serializer.data)
        except TdsReport.DoesNotExist:
            return Response({'error': 'TDS report not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_tds_reports(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = TdsReport.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No TDS reports found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = TdsReportSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = TdsReportSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        

class SalesTdsViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        tds_report_key = kwargs.get('pk')

        if tds_report_key:
            return self.retrieve_sales_tds_report(tds_report_key)

        return self.list_sales_tds_reports(request)

    def retrieve_sales_tds_report(self, tds_report_key):
        try:
            tds_report = SalesTds.objects.get(key=tds_report_key)
            serializer = SalesTdsSerializer(tds_report)
            return Response(serializer.data)
        except SalesTds.DoesNotExist:
            return Response({'error': 'Sales TDS report not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_sales_tds_reports(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = SalesTds.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No Sales TDS reports found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = SalesTdsSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = SalesTdsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class PurchaseGstEntryViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        purchase_gst_entry_key = kwargs.get('pk')

        if purchase_gst_entry_key:
            return self.retrieve_purchase_gst_entry(purchase_gst_entry_key)

        return self.list_purchase_gst_entries(request)

    def retrieve_purchase_gst_entry(self, purchase_gst_entry_key):
        try:
            purchase_gst_entry = PurchaseGstEntry.objects.get(key=purchase_gst_entry_key)
            serializer = PurchaseGstEntrySerializer(purchase_gst_entry)
            return Response(serializer.data)
        except PurchaseGstEntry.DoesNotExist:
            return Response({'error': 'Purchase Gst Entry not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_purchase_gst_entries(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = PurchaseGstEntry.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No Purchase Gst Entries found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = PurchaseGstEntrySerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = PurchaseGstEntrySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class PurchaseGstReportViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        purchase_gst_report_key = kwargs.get('pk')

        if purchase_gst_report_key:
            return self.retrieve_purchase_gst_report(purchase_gst_report_key)

        return self.list_purchase_gst_reports(request)

    def retrieve_purchase_gst_reportt(self, purchase_gst_report_key):
        try:
            purchase_gst_report = PurchaseGstReport.objects.get(key=purchase_gst_report_key)
            serializer = PurchaseGstReportSerializer(purchase_gst_report)
            return Response(serializer.data)
        except PurchaseGstReport.DoesNotExist:
            return Response({'error': 'Purchase Gst Report not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_purchase_gst_reports(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = PurchaseGstReport.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No Purchase Gst Reports found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = PurchaseGstReportSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = PurchaseGstReportSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class SalesGstEntryViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        sales_gst_entry_key = kwargs.get('pk')

        if sales_gst_entry_key:
            return self.retrieve_sales_gst_entry(sales_gst_entry_key)

        return self.list_sales_gst_entries(request)

    def retrieve_sales_gst_entry(self, sales_gst_entry_key):
        try:
            sales_gst_entry = SalesGstEntry.objects.get(key=sales_gst_entry_key)
            serializer = SalesGstEntrySerializer(sales_gst_entry)
            return Response(serializer.data)
        except SalesGstEntry.DoesNotExist:
            return Response({'error': 'Sales Gst Entry not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_sales_gst_entries(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = SalesGstEntry.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No Sales Gst Entries found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = SalesGstEntrySerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = SalesGstEntrySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


class SalesGstReportViewSet(APIView):

    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        sale_gst_report_key = kwargs.get('pk')

        if sale_gst_report_key:
            return self.retrieve_sales_gst_report(sale_gst_report_key)

        return self.list_sales_gst_reports(request)

    def retrieve_sales_gst_report(self, sale_gst_report_key):
        try:
            sales_gst_report = SalesGstReport.objects.get(key=sale_gst_report_key)
            serializer = SalesGstReportSerializer(sales_gst_report)
            return Response(serializer.data)
        except SalesGstReport.DoesNotExist:
            return Response({'error': 'Sales Gst Report not found'}, status=status.HTTP_404_NOT_FOUND)

    def list_sales_gst_reports(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = SalesGstReport.objects.filter(
            client=clientID, company=companyID).order_by('-key')

        month = request.GET.get('month')
        year = request.GET.get('year')

        if month and year:
            qrySet = qrySet.filter(date__month=month, date__year=year)

        if not qrySet.exists():
            return Response({'error': 'No Sales Gst Reports found for the specified month and year', 'data': []}, status=status.HTTP_200_OK)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = SalesGstReportSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qrySet, request)
            serializer = SalesGstReportSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
