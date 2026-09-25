from django.shortcuts import render
from pricing.models import Goodsreceiptnote, GoodsreceiptnoteItems
from pricing.serializers import GoodsReceiptNoteSerializer, GoodsReceiptNoteItemsSerializer
from inventory.models import Item, Itemuom
from vendor.models import Vendor
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from buildiq.pagenation_configs import Pagination10PerPage


class PurchaseInquiryViewset(viewsets.ViewSet):
    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectID = request.GET.get('project_id', False)
        if projectID:
            if Goodsreceiptnote.objects.filter(proj_key=projectID, client_id=clientID, company=companyID).exists():
                grnSerialiser = GoodsReceiptNoteSerializer(Goodsreceiptnote.objects.filter(
                    proj_key=projectID, client_id=clientID, company=companyID), many=True, fields=('key', 'number', 'date', 'vendor', 'vend_key'))

                data = []
                for grn in grnSerialiser.data:

                    grnKey = grn.get('key')
                    grnItemIns = GoodsreceiptnoteItems.objects.filter(
                        grn_key=grnKey)
                    grnItmSerialiser = GoodsReceiptNoteItemsSerializer(
                        grnItemIns, many=True, fields=('items', 'items_oums', 'qty', 'unitprice', 'netamt', 'taxamt', 'totalamt',)).data

                    for grnItms in grnItmSerialiser:
                        data.append(
                            {
                                "grn_number": grn['number'],
                                "grn_date": grn['date'],
                                "vendor": grn['vendor']['name'],
                                "item": grnItms['items']['descr'],
                                "item_oum": grnItms['items_oums']['descr'],
                                "qty": grnItms['qty'],
                                "unitprice": grnItms['unitprice'],
                                "netamt": grnItms['netamt'],
                                "taxamt": grnItms['taxamt'],
                                "totalamt": grnItms['totalamt']
                            }
                        )

                return Response(data)

            else:
                return Response([])

        return Response({"error": 1, "detail": "You need to pass project_id"})
