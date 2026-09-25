from rest_framework import status
from sale.models import SaleReceipt
from django.db.models import Sum, F, Q
from buildiq.utils import UtilFunctions
from salary_and_allowance.models import SalaryAndAllowance
from pricing.models import Vendorinvoice
from project.models import PaidExpenses
from rest_framework.views import APIView
from rest_framework.response import Response
from vendor.models import VendorPaymentVoucherDtl, VendorPaymentVoucherHdr
from rest_framework.generics import GenericAPIView
from buildiq.pagenation_configs import Pagination10PerPage
from contractor.models import ContractVoucherDtl, ContractorInvoice
from .serializers import VendorInvoiceReportSerializer, CustomerPaymentReceiptSerializer, ContractorPaymentVoucherSerializer, SupplierPaymentVoucherSerializer, ContractorTDSReportSerializer, PayrollReportSerializer, PaidExpenseReportSerializer, SupplierPaymentVoucherHdrSerializer
from datetime import datetime


class GSTVendorInvoiceViewSet(GenericAPIView):
    queryset = Vendorinvoice.objects.all()
    serializer_class = VendorInvoiceReportSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID, company_id=companyID, gstamt__gt=0).order_by('-createddttm')
        year = request.GET.get("year")
        month = request.GET.get("month")

        if year and month:
            queryset = queryset.filter(
                invoicedate__year=year, invoicedate__month=month)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(
                queryset, many=True, fields=[
                    'invoice_date', 'vendor_name', 'vendor_gst', 'material_type', 'taxable_invoice_amount', 'gst_rate', 'gst_amount', 'rounded_off_direction', 'rounded_off_value', 'total_bill_amount', 'vendor_invoice_no', 'project_name'])
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True, fields=[
                'invoice_date', 'vendor_name', 'vendor_gst', 'material_type', 'taxable_invoice_amount', 'gst_rate', 'gst_amount', 'rounded_off_direction', 'rounded_off_value', 'total_bill_amount', 'vendor_invoice_no', 'project_name'])
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset, many=True, fields=[
                'invoice_date', 'vendor_name', 'vendor_gst', 'material_type', 'taxable_invoice_amount', 'gst_rate', 'gst_amount', 'rounded_off_direction', 'rounded_off_value', 'total_bill_amount', 'vendor_invoice_no', 'project_name'])

        return Response(serializer.data, status=status.HTTP_200_OK)


class NonGSTVendorInvoiceViewSet(GenericAPIView):
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendor_qs = Vendorinvoice.objects.filter(
            client_id=clientID,
            company_id=companyID,
            gstamt__lte=0
        ).order_by('-createddttm')

        expense_qs = PaidExpenses.objects.filter(
            client_id=clientID,
            company_id=companyID
        ).order_by('-date')

        year = request.GET.get("year")
        month = request.GET.get("month")
        if year and month:
            vendor_qs = vendor_qs.filter(invoicedate__year=year, invoicedate__month=month)
            expense_qs = expense_qs.filter(date__year=year, date__month=month)

        without_pagination = request.GET.get("without_pagination", False)
        if without_pagination and int(without_pagination) == 1:
            vendor_data = VendorInvoiceReportSerializer(
                vendor_qs,
                many=True,
                fields=['invoice_date', 'vendor_name', 'material_type', 'total_bill_amount', 'project_name']
            ).data
            expense_data = PaidExpenseReportSerializer(expense_qs, many=True).data

            combined_data = vendor_data + expense_data
            combined_data.sort(key=lambda x: datetime.strptime(x['invoice_date'], "%d-%m-%Y"), reverse=True)

            return Response(combined_data)

        combined_list = list(vendor_qs) + list(expense_qs)
        combined_list.sort(key=lambda x: x.invoicedate if isinstance(x, Vendorinvoice) else x.date, reverse=True)

        page = self.paginate_queryset(combined_list)
        if page is not None:
            vendor_items = [obj for obj in page if isinstance(obj, Vendorinvoice)]
            expense_items = [obj for obj in page if isinstance(obj, PaidExpenses)]

            vendor_data = VendorInvoiceReportSerializer(
                vendor_items,
                many=True,
                fields=['invoice_date', 'vendor_name', 'material_type', 'total_bill_amount', 'project_name']
            ).data

            expense_data = PaidExpenseReportSerializer(expense_items, many=True).data

            combined_page_data = vendor_data + expense_data
            combined_page_data.sort(key=lambda x: datetime.strptime(x['invoice_date'], "%d-%m-%Y"), reverse=True)

            return self.get_paginated_response(combined_page_data)

        return Response([], status=status.HTTP_200_OK)


class CustomerPaymentReceiptReportViewSet(GenericAPIView):
    queryset = SaleReceipt.objects.all()
    serializer_class = CustomerPaymentReceiptSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID, company_id=companyID).order_by('-created_at')
        year = request.GET.get("year")
        month = request.GET.get("month")

        if year and month:
            queryset = queryset.filter(
                date__year=year, date__month=month)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(
                queryset, many=True, fields=[
                    'date_of_receipt', 'customer_name', 'receipt_amount', 'project_name', 'flat_name', 'sale_area', 'carpet_area', 'gross_value', 'mode_of_payment', 'project_location'])
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True, fields=[
                'date_of_receipt', 'customer_name', 'receipt_amount', 'project_name', 'flat_name', 'sale_area', 'carpet_area', 'gross_value', 'mode_of_payment', 'project_location'])
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset, many=True, fields=[
                'date_of_receipt', 'customer_name', 'receipt_amount', 'project_name', 'flat_name', 'sale_area', 'carpet_area', 'gross_value', 'mode_of_payment', 'project_location'])

        return Response(serializer.data, status=status.HTTP_200_OK)


class ContractorPaymentVoucherReportViewSet(GenericAPIView):
    queryset = ContractVoucherDtl.objects.all()
    serializer_class = ContractorPaymentVoucherSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            contract_voucher_hdr__client_id=clientID, contract_voucher_hdr__company_id=companyID).order_by('-contract_voucher_hdr__contract_voucher_dt')
        year = request.GET.get("year")
        month = request.GET.get("month")

        if year and month:
            queryset = queryset.filter(
                contract_voucher_hdr__contract_voucher_dt__year=year, contract_voucher_hdr__contract_voucher_dt__month=month)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(
                queryset, many=True, fields=[
                    'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'contractor_type'])
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True, fields=[
                'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'contractor_type'])
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset, many=True, fields=[
                'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'contractor_type'])

        return Response(serializer.data, status=status.HTTP_200_OK)


class SupplierPaymentVoucherReportViewSet(GenericAPIView):
    queryset = VendorPaymentVoucherDtl.objects.all()
    serializer_class = SupplierPaymentVoucherSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            vendor_voucher_hdr__client_id=clientID, vendor_voucher_hdr__company_id=companyID).order_by('-vendor_voucher_hdr__vendor_voucher_dt')
        year = request.GET.get("year")
        month = request.GET.get("month")

        if year and month:
            queryset = queryset.filter(
                vendor_voucher_hdr__vendor_voucher_dt__year=year, vendor_voucher_hdr__vendor_voucher_dt__month=month)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(
                queryset, many=True, fields=[
                    'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'vendor_type'])
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True, fields=[
                'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'vendor_type'])
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset, many=True, fields=[
                'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'vendor_type'])

        return Response(serializer.data, status=status.HTTP_200_OK)


class ContractorTDSReportViewSet(GenericAPIView):
    queryset = ContractVoucherDtl.objects.select_related(
        'contract_voucher_hdr__contractor_id',
        'invoice_id'
    )
    serializer_class = ContractorTDSReportSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        voucher_filter = Q(
            contract_voucher_hdr__client_id=clientID,
            contract_voucher_hdr__company_id=companyID
        )

        year = request.GET.get("year")
        month = request.GET.get("month")
        if year and month:
            voucher_filter &= Q(
                contract_voucher_hdr__contract_voucher_dt__year=year,
                contract_voucher_hdr__contract_voucher_dt__month=month
            )

        invoice_ids = ContractVoucherDtl.objects.filter(voucher_filter)\
            .values_list('invoice_id', flat=True).distinct()

        invoices = ContractorInvoice.objects.filter(
            key__in=invoice_ids,
            tds_amount__isnull=False,
            tds_amount__gt=0
        ).select_related('contractor_id')

        grouped_data = invoices.values(
            contractor_name=F('contractor_id__name'),
            pan_no=F('contractor_id__pan_no')
        ).annotate(
            amount=Sum('tds_amount')
        ).order_by('contractor_name')

        page = self.paginate_queryset(grouped_data)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(grouped_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PayrollReportViewSet(GenericAPIView):
    queryset = SalaryAndAllowance.objects.all()
    serializer_class = PayrollReportSerializer
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID, company_id=companyID).order_by('-date')

        year = request.GET.get("year")
        month = request.GET.get("month")
        if year and month:
            queryset = queryset.filter(
                date__year=year, date__month=month)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(
                queryset, many=True, fields=['date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'type', 'project'])
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True, fields=[
                                               'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'type', 'project'])
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True, fields=[
                                           'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'type', 'project'])
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportReportViewSet(APIView):
    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        year = request.GET.get("year")
        month = request.GET.get("month")

        VALID_KEYS = {
            'gst_invoices',
            'non_gst_invoices',
            'customer_payments',
            'contractor_payments',
            'supplier_payments',
            'payroll_reports',
            'contractor_tds'
        }

        includes_raw = request.GET.get("include", None)

        if includes_raw is None or includes_raw.strip() == "":
            return Response({
                "error": "Missing 'include' parameter.",
                "message": "You must specify at least one report to include using the 'include' query parameter.",
                "valid_options": list(VALID_KEYS)
            }, status=status.HTTP_400_BAD_REQUEST)

        includes = [key.strip()
                    for key in includes_raw.split(",") if key.strip()]

        invalid_keys = [key for key in includes if key not in VALID_KEYS]
        if invalid_keys:
            return Response({
                "error": "Invalid report types requested.",
                "invalid_keys": invalid_keys,
                "valid_options": list(VALID_KEYS)
            }, status=status.HTTP_400_BAD_REQUEST)

        def filter_by_date(queryset, field_name):
            if year and month:
                filter_kwargs = {
                    f"{field_name}__year": year,
                    f"{field_name}__month": month
                }
                return queryset.filter(**filter_kwargs)
            return queryset

        response_data = {}

        if 'gst_invoices' in includes:
            gst_queryset = Vendorinvoice.objects.filter(
                client_id=clientID, company_id=companyID, gstamt__gt=0
            ).order_by('-createddttm')
            gst_queryset = filter_by_date(gst_queryset, 'invoicedate')
            response_data['gst_invoices'] = VendorInvoiceReportSerializer(
                gst_queryset, many=True, fields=[
                    'invoice_date', 'vendor_name', 'vendor_gst', 'material_type', 'taxable_invoice_amount', 'gst_rate', 'gst_amount', 'rounded_off_direction', 'rounded_off_value', 'total_bill_amount', 'vendor_invoice_no', 'project_name']
            ).data

        if 'non_gst_invoices' in includes:
            non_gst_queryset = Vendorinvoice.objects.filter(
                client_id=clientID, company_id=companyID, gstamt__lte=0
            ).order_by('-createddttm')

            expense_qs = PaidExpenses.objects.filter(
                client_id=clientID,
                company_id=companyID
            ).order_by('-date')

            non_gst_queryset = filter_by_date(non_gst_queryset, 'invoicedate')
            expense_qs = filter_by_date(expense_qs, 'date')
            non_gst_data = VendorInvoiceReportSerializer(
                non_gst_queryset, many=True, fields=[
                    'invoice_date', 'vendor_name', 'material_type', 'total_bill_amount', 'project_name']
            ).data
            expense_data = PaidExpenseReportSerializer(expense_qs, many=True).data
            combined_data = non_gst_data + expense_data
            combined_data.sort(key=lambda x: datetime.strptime(x['invoice_date'], "%d-%m-%Y"), reverse=True)
            response_data['non_gst_invoices'] =  combined_data

        if 'customer_payments' in includes:
            receipt_queryset = SaleReceipt.objects.filter(
                client_id=clientID, company_id=companyID
            ).order_by('-created_at')
            receipt_queryset = filter_by_date(receipt_queryset, 'date')
            response_data['customer_payments'] = CustomerPaymentReceiptSerializer(
                receipt_queryset, many=True, fields=[
                    'date_of_receipt', 'customer_name', 'receipt_amount', 'project_name', 'flat_name', 'sale_area', 'carpet_area', 'gross_value', 'mode_of_payment', 'project_location']
            ).data

        if 'contractor_payments' in includes:
            contractor_queryset = ContractVoucherDtl.objects.filter(
                contract_voucher_hdr__client_id=clientID,
                contract_voucher_hdr__company_id=companyID
            ).order_by('-contract_voucher_hdr__contract_voucher_dt')
            contractor_queryset = filter_by_date(
                contractor_queryset, 'contract_voucher_hdr__contract_voucher_dt')
            response_data['contractor_payments'] = ContractorPaymentVoucherSerializer(
                contractor_queryset, many=True, fields=[
                    'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'contractor_type']
            ).data

        if 'supplier_payments' in includes:
            supplier_queryset = VendorPaymentVoucherHdr.objects.filter(
                client_id=clientID,
                company_id=companyID
            ).order_by('-vendor_voucher_dt')
            supplier_queryset = filter_by_date(
                supplier_queryset, 'vendor_voucher_dt')
            response_data['supplier_payments'] = SupplierPaymentVoucherHdrSerializer(
                supplier_queryset, many=True, fields=[
                    'date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'vendor_type']
            ).data

        if 'payroll_reports' in includes:
            payroll_queryset = SalaryAndAllowance.objects.filter(
                client_id=clientID, company_id=companyID,
            ).order_by('-date')
            payroll_queryset = filter_by_date(payroll_queryset, 'date')
            response_data['payroll'] = PayrollReportSerializer(
                payroll_queryset, many=True, fields=['date_of_payment', 'payee_name', 'amount', 'mode_of_payment', 'bank_name', 'transaction_no', 'type', 'project']).data

        if 'contractor_tds' in includes:
            voucher_filter = Q(
                contract_voucher_hdr__client_id=clientID,
                contract_voucher_hdr__company_id=companyID
            )

            if year and month:
                voucher_filter &= Q(
                    contract_voucher_hdr__contract_voucher_dt__year=year,
                    contract_voucher_hdr__contract_voucher_dt__month=month
                )

            invoice_ids = ContractVoucherDtl.objects.filter(voucher_filter)\
                .values_list('invoice_id', flat=True).distinct()

            invoices = ContractorInvoice.objects.filter(
                key__in=invoice_ids,
                tds_amount__isnull=False,
                tds_amount__gt=0
            ).select_related('contractor_id')

            grouped_data = invoices.values(
                contractor_name=F('contractor_id__name'),
                pan_no=F('contractor_id__pan_no')
            ).annotate(
                amount=Sum('tds_amount')
            ).order_by('contractor_name')

            response_data['contractor_tds'] = ContractorTDSReportSerializer(
                grouped_data, many=True
            ).data

        return Response(response_data, status=status.HTTP_200_OK)
