from rest_framework import status
from collections import defaultdict
from project.models import PaidExpenses
from buildiq.utils import UtilFunctions
from rest_framework.views import APIView
from rest_framework.response import Response
from contractor.models import ContractorInvoice
from rest_framework.generics import GenericAPIView
from buildiq.pagenation_configs import Pagination10PerPage
from salary_and_allowance.models import SalaryAndAllowance
from pricing.models import Vendorinvoice, PurchaseorderItems, Purchaseorder
from .serializers import MaterialExpenseSerializer, ContractExpenseSerializer, SalaryExpenseSerializer, ExtraExpenseSerializer, StockItemSerializer
from collections import defaultdict


class MaterialExpenseApiViewSet(GenericAPIView):
    serializer_class = MaterialExpenseSerializer
    pagination_class = Pagination10PerPage  # optional

    def get(self, request, *args, **kwargs):
        try:
            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)
            project_id = request.GET.get("project_id")

            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            invoices = Vendorinvoice.objects.filter(
                company=company_id,
                client_id=client_id,
                proj_key=project_id,
                po_key__isnull=False
            )

            data = []

            for invoice in invoices:
                try:
                    data.append({
                        "item_type": invoice.po_key.item_type_key.descr,
                        "netamt": float(invoice.netamt or 0),
                        "paid_amount": float(invoice.paid_amount or 0),
                        "discount_amount": float(invoice.discountamt or 0),
                    })
                except Exception as e:
                    print(
                        f"Error processing invoice {invoice.po_key}: {str(e)}")
                    continue

            grouped_data = defaultdict(
                lambda: {"netamt": 0.0, "paid_amount": 0.0, "discount_amount": 0.0})
            print("data ::", data)
            for d in data:
                grouped_data[d["item_type"]]["netamt"] += d["netamt"]
                grouped_data[d["item_type"]]["paid_amount"] += d["paid_amount"]
                grouped_data[d["item_type"]]["discount_amount"] += d["discount_amount"]
            print("grouped_data ::", grouped_data)

            result = [
                {
                    "item_type": item_type,
                    "netamt": round(values["netamt"], 2),
                    "paid_amount": round(values["paid_amount"], 2),
                    "discount_amount": round(values["discount_amount"], 2),
                }
                for item_type, values in grouped_data.items()
            ]

            print("result ::", result)

            # Optional pagination support
            if request.GET.get("without_pagination") == "1":
                serializer = self.get_serializer(result, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(result)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error in MaterialExpenseApiViewSet: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContractExpenseApiViewSet(GenericAPIView):
    serializer_class = ContractExpenseSerializer
    # Optional, use your custom class if needed
    pagination_class = Pagination10PerPage

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET.get("project_id")
            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)

            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            invoices = ContractorInvoice.objects.filter(
                company_id=company_id,
                client_id=client_id,
                project_id=project_id
            )

            data = []

            for invoice in invoices:
                try:
                    contractor_type = invoice.contractor_id.contractortyp_key.descr
                    data.append({
                        "contractor_type": contractor_type,
                        "invamt": float(invoice.invoice_amount or 0),
                        "paid_amount": float(invoice.paid_amount or 0),
                    })
                except Exception as e:
                    print(
                        f"Error processing contractor invoice {invoice.invoice_desc}: {str(e)}")
                    continue

            grouped_data = defaultdict(
                lambda: {"invamt": 0.0, "paid_amount": 0.0})
            for d in data:
                grouped_data[d["contractor_type"]]["invamt"] += d["invamt"]
                grouped_data[d["contractor_type"]
                             ]["paid_amount"] += d["paid_amount"]

            result = [
                {
                    "contractor_type": contractor_type,
                    "invoice_amount": round(values["invamt"], 2),
                    "paid_amount": round(values["paid_amount"], 2),
                }
                for contractor_type, values in grouped_data.items()
            ]

            # Handle optional no-pagination mode
            if request.GET.get("without_pagination") == "1":
                serializer = self.get_serializer(result, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(result)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error in ContractExpenseApiViewSet: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalaryExpenseApiViewSet(GenericAPIView):
    serializer_class = SalaryExpenseSerializer
    pagination_class = Pagination10PerPage  # Optional

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET.get("project_id")

            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)
            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            salary_expenses = SalaryAndAllowance.objects.filter(
                company_id=company_id,
                client_id=client_id,
                project_key=project_id
            )

            data = []

            for salary_expense in salary_expenses:
                try:
                    employee = salary_expense.employee.first_name
                    expense_type = 'Salary' if salary_expense.type == 'S' else 'Allowance'
                    data.append({
                        "employee": employee,
                        "expense_type": expense_type,
                        "amount": float(salary_expense.amount or 0),
                    })
                except Exception as e:
                    print(
                        f"Error processing salary expense {salary_expense.key}: {str(e)}")
                    continue

            grouped_data = defaultdict(
                lambda: {"salary": 0.0, "allowance": 0.0})
            for d in data:
                if d["expense_type"] == 'Salary':
                    grouped_data[d["employee"]]["salary"] += d["amount"]
                else:
                    grouped_data[d["employee"]]["allowance"] += d["amount"]

            result = [
                {
                    "employee": employee,
                    "salary": round(values["salary"], 2),
                    "allowance": round(values["allowance"], 2),
                }
                for employee, values in grouped_data.items()
            ]

            if request.GET.get("without_pagination") == "1":
                serializer = self.get_serializer(result, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(result)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error in SalaryExpenseApiViewSet: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExtraExpenseApiViewSet(GenericAPIView):
    serializer_class = ExtraExpenseSerializer
    pagination_class = Pagination10PerPage  # Optional

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET.get("project_id")

            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)
            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            expenses = PaidExpenses.objects.filter(
                company_id=company_id,
                client_id=client_id,
                project_key=project_id
            )

            data = []

            for expense in expenses:
                try:
                    expense_type_descr = expense.expense_type.descr
                    data.append({
                        "expense_type": expense_type_descr,
                        "amount": float(expense.amount or 0),
                    })
                except Exception as e:
                    print(f"Error processing expense {expense.key}: {str(e)}")
                    continue

            grouped_data = defaultdict(float)
            for d in data:
                grouped_data[d["expense_type"]] += d["amount"]

            result = [
                {
                    "expense_type": expense_type,
                    "paid_amount": round(amount, 2),
                }
                for expense_type, amount in grouped_data.items()
            ]

            # Handle without pagination
            if request.GET.get("without_pagination") == "1":
                serializer = self.get_serializer(result, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(result)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error in ExtraExpenseApiViewSet: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverallExpenseApiViewSet(APIView):
    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET.get("project_id")
            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)

            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            # Initialize totals
            material_invoice_total = 0.0
            material_paid_total = 0.0
            contract_invoice_total = 0.0
            contract_paid_total = 0.0
            extra_paid_total = 0.0
            salary_total = 0.0
            allowance_total = 0.0

            # Material Expenses
            material_invoices = Vendorinvoice.objects.filter(
                company=company_id, client_id=client_id, proj_key=project_id
            )
            for invoice in material_invoices:
                try:
                    material_invoice_total += float(invoice.netamt or 0)
                    material_paid_total += float(invoice.paid_amount or 0)
                except:
                    continue

            # Contract Expenses
            contractor_invoices = ContractorInvoice.objects.filter(
                company_id=company_id, client_id=client_id, project_id=project_id
            )
            for invoice in contractor_invoices:
                try:
                    contract_invoice_total += float(
                        invoice.invoice_amount or 0)
                    contract_paid_total += float(invoice.paid_amount or 0)
                except:
                    continue

            # Extra Expenses
            extra_expenses = PaidExpenses.objects.filter(
                company_id=company_id, client_id=client_id, project_key=project_id
            )
            for expense in extra_expenses:
                try:
                    extra_paid_total += float(expense.amount or 0)
                except:
                    continue

            # Salary and Allowance Expenses
            salary_expenses = SalaryAndAllowance.objects.filter(
                company_id=company_id, client_id=client_id, project_key=project_id
            )
            for s_expense in salary_expenses:
                try:
                    if s_expense.type == 'S':
                        salary_total += float(s_expense.amount or 0)
                    else:
                        allowance_total += float(s_expense.amount or 0)
                except:
                    continue

            # Final response
            return Response({
                "material_expense": {
                    "netamt": round(material_invoice_total, 2),
                    "paid_amount": round(material_paid_total, 2),
                },
                "contract_expense": {
                    "invoice_amount": round(contract_invoice_total, 2),
                    "paid_amount": round(contract_paid_total, 2),
                },
                "extra_expense": {
                    "paid_amount": round(extra_paid_total, 2),
                },
                "salary_expense": {
                    "salary_amount": round(salary_total, 2),
                    "allowance_amount": round(allowance_total, 2),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(
                f"Unexpected error in TotalProjectExpenseApiViewSet: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StockListApiViewSet(GenericAPIView):
    serializer_class = StockItemSerializer
    pagination_class = Pagination10PerPage

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.GET.get("project_id")
            item_type = request.GET.get("item_type")

            UF = UtilFunctions()
            is_valid, return_obj, client_id, company_id = UF.getClientInfo(
                request)
            if not is_valid:
                return Response(return_obj['message'], status=return_obj['http_status'])

            invoices = Vendorinvoice.objects.filter(
                company=company_id, client_id=client_id, proj_key=project_id, po_key__isnull=False, paid_amount__gt=0)
            
            if item_type:
                invoices = invoices.filter(po_key__item_type_key=item_type)

            grouped_data = defaultdict(lambda: {
                "item_key": None,
                "item_name": "",
                "item_type": "",
                "quantity": 0.0,
                "UOM": "",
                "model": "",
                "brand": "",
                "invoices": [],
            })

            for inv in invoices:
                try:
                    purchase_order_items = PurchaseorderItems.objects.filter(po_key=inv.po_key)
                    for po_item in purchase_order_items:
                        key = po_item.item_key.key

                        item_data = grouped_data[key]
                        item_data["item_key"] = key
                        item_data["item_name"] = po_item.item_key.descr
                        item_data["item_type"] = po_item.item_key.itemtyp_key.descr
                        item_data["quantity"] += float(po_item.qty or 0)
                        item_data["UOM"] = po_item.item_uom_key.descr if po_item.item_uom_key else None
                        item_data["model"] = po_item.model_number
                        item_data["brand"] = po_item.brand
                        item_data["invoices"].append({
                            "invoice_key": inv.key,
                            "date": inv.invoicedate,
                            "invoice_no": inv.invoiceno,
                            "quantity": float(po_item.qty or 0),
                            "uom": po_item.item_uom_key.descr if po_item.item_uom_key else None
                        })


                except Exception as invoice_error:
                    print(f"Error processing purchase order {inv.po_key}: {str(invoice_error)}")
                    return Response({"error": "Error While Processing Item From Invoice", "value": str(invoice_error)}, status=500)

            response_data = []
            for item in grouped_data.values():
                response_data.append({
                    "item_key": item["item_key"],
                    "item_name": item["item_name"],
                    "item_type": item["item_type"],
                    "quantity": item["quantity"],
                    "UOM": item["UOM"],
                    "model": item["model"],
                    "brand": item["brand"],
                    "invoices": item["invoices"]
                })

            if request.GET.get("without_pagination") == "1":
                serializer = self.get_serializer(response_data, many=True)
                return Response(serializer.data)

            # Paginate data
            page = self.paginate_queryset(response_data)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(response_data, many=True)
            return Response(serializer.data)

        except Exception as e:
            print(f"Unexpected error in StockListApiViewSet :: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=500)
