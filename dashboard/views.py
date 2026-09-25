from rest_framework.response import Response
from rest_framework.views import APIView
from project.models import Project
from pricing.models import Purchaseorder, Vendorinvoice
from contractor.models import ContractorInvoice
from buildiq.utils import UtilFunctions

class DashboardSummary(APIView):
    def get(self, request):
        UF=UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid: 
            return Response(returnObj["message"], status=returnObj["http_status"])
        data = {
            "active_projects": Project.objects.filter(client_id=clientID, company_id=companyID).count(),
            "pending_pos" : Purchaseorder.objects.filter(status="O",client_id=clientID, company_id = companyID).count(),
            "vendor_pending_payments": Vendorinvoice.objects.filter(invoice_status__in=["O", "A"], client_id=clientID, company_id=companyID).count(),
            "contractor_pending_payments": ContractorInvoice.objects.filter(invoice_status__in=["O", "A"], client_id=clientID, company_id=companyID).count()
        }
        return Response(data)