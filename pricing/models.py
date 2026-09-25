from django.db import models
from client.models import Company, Clientbase
from vendor.models import Vendor, Apterms
from project.models import Project
from inventory.models import Warehouse, Item, Itemuom, Itemtype, Brand
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from contractor.models import (
    Vendorcontract, VendorcontractStages, VendorcontractTasks)
from inventory.models import Itemtype


class InvoiceManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

    def saveInvoice(self, params, serializer):

        if not params.get('invoicedate', False):
            return {}, False, "Invoice Date (invoicedate) Missing", {}
        if params.get('apterm_key', False) and not Apterms.objects.filter(key=params.get('apterm_key')).exists():
            return {}, False, "Invalid Ap Term (apterm_key)", {}

        # CALCULATE DATES
        if not params.get('apterm_key', False):
            apterm_days = 0
        else:
            apterm_days = Apterms.objects.get(
                key=params.get('apterm_key')).days

        params['apterm_days'] = apterm_days
        invoicedate = params.get('invoicedate')
        invoicedateObj = datetime.strptime(
            invoicedate, '%Y-%m-%d')
        dueDate = invoicedateObj + timedelta(days=int(apterm_days))
        params['duedate'] = dueDate.strftime('%Y-%m-%d')

        serializerIns = serializer(data=params)
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Vendor Invoice Added Successfully", {}
            except:
                return {}, False, "Error While Adding Vendor Invoice", {}

        return {}, False, "Error in API request", serializerIns.errors

    def invoiceUpdate(self, params, serializer, VendinvceKey, additionalParams={}):
        VendinvceIns = get_object_or_404(self.get_queryset(), pk=VendinvceKey)
        try:

            if params.get('apterm_key', False) and not Apterms.objects.filter(key=params.get('apterm_key')).exists():
                return {}, False, "Invalid Ap Term (apterm_key)", {}

            if not params.get('apterm_key', False):
                apterm_days = 0
            else:
                apterm_days = Apterms.objects.get(
                    key=params.get('apterm_key')).days

            apterm_day = params['apterm_days']
            invoicedate = params.get('invoicedate')
            invoicedateObj = datetime.strptime(
                invoicedate, '%Y-%m-%d')
            dueDate = invoicedateObj + timedelta(days=int(apterm_days))
            params['duedate'] = dueDate.strftime('%Y-%m-%d')
            params.update(additionalParams)

            serializerIns = serializer(
                VendinvceIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    return serializerIns.data, True, "Vendor Invoice Updated Successfully", {}
                except:
                    return {}, False, "Error In Vendor Invoice PUT Request", {}
            else:
                return {}, False, "Error In Vendor Invoice PUT Request", serializerIns.errors
        except Exception as e:
            return {}, False, "Please check apterm_key and invoicedate", {}

    def submitInvoice(self, params, pk, serializer):
        modelIns, updateStatus, msg, data = self.invoiceUpdate(
            params, serializer, pk, {})
        return modelIns, updateStatus, msg, data

    def cancelInvoice(self, pk, serializer):
        otherTableUpdateReq = True
        VendinvceIns = get_object_or_404(self.get_queryset(), pk=pk)

        if VendinvceIns.docstatus == "S":
            VendinvceIns.docstatus = "C"
            otherTableUpdateReq = False
        elif VendinvceIns.docstatus == "U":
            VendinvceIns.docstatus = "C"
            otherTableUpdateReq = True

        VendinvceIns.save()
        return serializer(VendinvceIns).data, True, "Invoice Update Success", {}, otherTableUpdateReq

    def doOtherTableUpdatesForVendorInvoice(self, venInvSeri, params, action, invoiceId):
        VendinvceIns = get_object_or_404(self.get_queryset(), pk=invoiceId)

        # VENDOR INVOICE CHAGES
        invoiceParams = {
            "balamt": VendinvceIns.invamt
        }
        if action == "CANCEL":
            invoiceParams['cancelledby'] = params['current_user']
            invoiceParams['cancelleddttm'] = params['current_date']
            invoiceParams['docstatus'] = "C"
        else:
            invoiceParams['submittedby'] = params['current_user']
            invoiceParams['submitteddttm'] = params['current_date']
            invoiceParams['docstatus'] = "U"

        invoiceParams['lastmodifiedby'] = params['current_user']
        invoiceParams['lastmodifieddttm'] = params['current_date']

        venInvSeriIns = venInvSeri(
            VendinvceIns, data=invoiceParams, partial=True)
        if venInvSeriIns.is_valid():
            venInvSeriIns.save()

        # GOOD RECEIPTS NOTES
        # if not Goodsreceiptnote.objects.filter(pk=VendinvceIns.grn_key).exists():
        #     # ROLL BACK EVERYTHING
        #     VendorinvoiceItems.objects.filter(vendinv_key=invoiceId).delete()
        #     Vendorinvoice.objects.get(key=invoiceId).delete()
        #     return False
        if Goodsreceiptnote.objects.filter(pk=VendinvceIns.grn_key).exists():
            grnIns = Goodsreceiptnote.objects.get(pk=VendinvceIns.grn_key)
            grnIns.lastmodifiedby = params['current_user']
            grnIns.lastmodifieddttm = params['current_date']

            if action == "CANCEL":
                grnIns.docstatus = "U"
                grnIns.vendinv_key = None
            else:
                grnIns.docstatus = "I"
                grnIns.vendinv_key = invoiceId
            grnIns.save()

        if action == "CANCEL":
            invAmount = float(venInvSeriIns.data['invamt']) * -1
            doclinekey = -1
        else:
            doclinekey = 1
            invAmount = float(venInvSeriIns.data['invamt'])

        vndrLdgr = VendorLedger(
            vend_key=venInvSeriIns.data['vend_key'],
            docid=venInvSeriIns.data['docid'],
            dockey=venInvSeriIns.data['key'],
            doclinekey=doclinekey,
            docnumber=venInvSeriIns.data['invoiceno'],
            docdate=venInvSeriIns.data['invoicedate'],
            notes="VoucherNo: "+str(venInvSeriIns.data['vouchno']),
            amt=invAmount,
            createdby=params['current_user'],
            createddttm=params['current_date'],
            company_id=venInvSeriIns.data['company'],
            client_id=venInvSeriIns.data['client_id']
        )
        vndrLdgr.save()
        return True

    def doOtherTableUpdatesForContractInvoice(self, venInvSeri, params, action, invoiceId, contractID):
        VendinvceIns = get_object_or_404(self.get_queryset(), pk=invoiceId)

        # VENDOR INVOICE CHAGES
        invoiceParams = {
            "balamt": VendinvceIns.invamt
        }
        if action == "CANCEL":
            invoiceParams['cancelledby'] = params['current_user']
            invoiceParams['cancelleddttm'] = params['current_date']
            invoiceParams['docstatus'] = "C"
        else:
            invoiceParams['submittedby'] = params['current_user']
            invoiceParams['submitteddttm'] = params['current_date']
            invoiceParams['docstatus'] = "U"

        invoiceParams['lastmodifiedby'] = params['current_user']
        invoiceParams['lastmodifieddttm'] = params['current_date']

        venInvSeriIns = venInvSeri(
            VendinvceIns, data=invoiceParams, partial=True)
        if venInvSeriIns.is_valid():
            venInvSeriIns.save()

        # VendorContract_Stages
        conStages = VendorcontractStages.objects.filter(vendctr_key=contractID)
        if action == "CANCEL":
            invoiceStatus = None
        else:
            invoiceStatus = "I"

        for stg in conStages:
            stg.Invoiced = invoiceStatus
            stg.lastmodifiedby = params['current_user']
            stg.lastmodifieddttm = params['current_date']
            stg.save()

        # VendorContract
        vendContrctIns = Vendorcontract.objects.get(key=contractID)
        vendContrctIns.docstatus = "U"
        vendContrctIns.lastmodifiedby = params['current_user']
        vendContrctIns.lastmodifieddttm = params['current_date']
        vendContrctIns.save()

        # Vendor_Ledger
        if action == "CANCEL":
            invAmount = float(venInvSeriIns.data['invamt']) * -1
            doclinekey = -1
        else:
            doclinekey = 1
            invAmount = float(venInvSeriIns.data['invamt'])

        vndrLdgr = VendorLedger(
            vend_key=venInvSeriIns.data['vend_key'],
            docid=venInvSeriIns.data['docid'],
            dockey=venInvSeriIns.data['key'],
            doclinekey=doclinekey,
            docnumber=venInvSeriIns.data['invoiceno'],
            docdate=venInvSeriIns.data['invoicedate'],
            notes="VoucherNo: "+str(venInvSeriIns.data['vouchno']),
            amt=invAmount,
            createdby=params['current_user'],
            createddttm=params['current_date'],
            company_id=venInvSeriIns.data['company'],
            client_id=venInvSeriIns.data['client_id']
        )
        vndrLdgr.save()
        return True

    def deleteAllInvoiceItemByInvoiceID(self, invoiceID):
        VendorinvoiceItems.objects.filter(vendinv_key=invoiceID).delete()

    def deleteInvoiceByInvoiceID(self, invoiceID):
        Vendorinvoice.objects.get(key=invoiceID).delete()

    def insertInvoiceItems(self, params, invItmSerialiser):
        invoiceId = params.get("invoice_id", False)
        company = params.get("company", False)
        client_id = params.get("client_id", False)
        user = params.get("user")

        # Removing all items first
        self.deleteAllInvoiceItemByInvoiceID(invoiceId)

        if invoiceId and company and client_id:
            insertedData = []
            invoiceItems = params.get('invoice_items', [])
            for item in invoiceItems:
                item['vendinv_key'] = invoiceId
                item['company'] = company
                item['client_id'] = client_id
                item['createdby'] = user
                serializer = invItmSerialiser(data=item)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        # if any one invoice items failed to load, delete all invoice items
                        self.deleteAllInvoiceItemByInvoiceID(invoiceId)
                        return {}, False, "Error in API request", serializer.errors
                except:
                    # if any one invoice items failed to load, delete all invoice items
                    self.deleteAllInvoiceItemByInvoiceID(invoiceId)
                    return {}, False, "Error While Adding Invoice Items1", {}

            if len(insertedData) == len(invoiceItems):
                return insertedData, True, "Invoice Items Modified Successfully", {}
            else:
                # if any one invoice items failed to load, delete all invoice items
                self.deleteAllInvoiceItemByInvoiceID(invoiceId)
                return {}, False, "Error While Adding Invoice Items", {}
        else:
            return {}, False, "Invoice number (or) company (or) client_id is missing", {}


class POManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

    def savePurOrdr(self, params, serializer):
        serializerIns = serializer(data=params)
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Purchase Order Added Successfully", {}
            except:
                return {}, False, "Error While Adding Purchase Order", {}

        return {}, False, "Error in API request", serializerIns.errors

    def purOrdrUpdate(self, params, serializer, poID, additionalParams={}):
        poIns = get_object_or_404(self.get_queryset(), pk=poID)
        try:
            serializerIns = serializer(
                poIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    return serializerIns.data, True, "Purchase Order Updated Successfully", {}
                except:
                    return {}, False, "Error In Purchase Order PUT Request", {}
            else:
                return {}, False, "Error In Purchase Order PUT Request", serializerIns.errors
        except Exception as e:
            return {}, False, "Please check request data", {}

    def submitPurOrdr(self, params, pk, serializer):
        modelIns, updateStatus, msg, data = self.purOrdrUpdate(
            params, serializer, pk, {})
        return modelIns, updateStatus, msg, data

    def cancelPurOrdr(self, pk, serializer):
        poIns = get_object_or_404(self.get_queryset(), pk=pk)
        poIns.docstatus = "C"
        poIns.save()
        return serializer(poIns).data, True, "Purchase Order Update Success", {}

    def deleteAllPoItemByPoID(self, poID):
        PurchaseorderItems.objects.filter(po_key=poID).delete()

    def deletePoByPoID(self, poID):
        Purchaseorder.objects.get(key=poID).delete()

    def insertPurOrdrItems(self, params, itmSerialiser):
        poID = params.get("po_id", False)
        company = params.get("company", False)
        client_id = params.get("client_id", False)
        user = params.get("user")
        date = params.get("createddate")

        # Removing all items first
        self.deleteAllPoItemByPoID(poID)

        if poID and company and client_id:
            insertedData = []
            poItems = params.get('purchs_odr_items', [])
            for item in poItems:
                item['po_key'] = poID
                item['company'] = company
                item['client_id'] = client_id
                item['createdby'] = user
                item['createdby'] = date
                serializer = itmSerialiser(data=item)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        # if any one PO item failed to load, delete all PO item
                        self.deleteAllPoItemByPoID(poID)
                        return {}, False, "Error in API request", serializer.errors
                except:
                    # if any one PO item failed to load, delete all PO item
                    self.deleteAllPoItemByPoID(poID)
                    return {}, False, "Error While Adding Purchase Order Items", {}

            if len(insertedData) == len(poItems):
                return insertedData, True, "Purchase Order Items Modified Successfully", {}
            else:
                # if any one PO item failed to load, delete all PO item
                self.deleteAllPoItemByPoID(poID)
                return {}, False, "Error While Adding Invoice Items", {}
        else:
            return {}, False, "Purchase Order number (or) company (or) client_id is missing", {}


class GRNManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

    def saveGRN(self, params, serializer):
        serializerIns = serializer(data=params)
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Material Purchase Added Successfully", {}
            except:
                return {}, False, "Error While Adding Material Purchase", {}

        return {}, False, "Error in API request", serializerIns.errors

    def grnUpdate(self, params, serializer, grnID, additionalParams={}):
        try:
            grnIns = get_object_or_404(self.get_queryset(), pk=grnID)
            params.update(additionalParams)
            serializerIns = serializer(
                grnIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    return serializerIns.data, True, "Material Purchase Updated Successfully", {}
                except:
                    return {}, False, "Error In Material Purchase PUT Request", {}
            else:
                return {}, False, "Error In Material Purchase PUT Request", serializerIns.errors
        except Exception as e:
            return {}, False, "Something went wrong", {}

    def submitGRN(self, params, pk, serializer):
        modelIns, updateStatus, msg, data = self.grnUpdate(
            params, serializer, pk, {})
        return modelIns, updateStatus, msg, data

    def cancelGRN(self, pk, serializer):
        otherTableUpdateReq = True
        if Goodsreceiptnote.objects.filter(pk=pk).exists():
            grnIns = Goodsreceiptnote.objects.get(pk=pk)
            grn_docstatus = grnIns.docstatus
            if grn_docstatus and grn_docstatus == "S":
                otherTableUpdateReq = False
            grnIns.docstatus = "C"
            grnIns.save()
            return serializer(grnIns).data, True, "GRN CANCELED", {}, otherTableUpdateReq

    def doOtherTableUpdates(self, grnSeril, params, action, grnKey, grnItems):
        grnIns = get_object_or_404(self.get_queryset(), pk=grnKey)
        grnParams = {}

        # try:
        if action == "CANCEL":
            # TODO checkm stock on hand before other process whethere we have qty to reduce

            # Material Purchase grnParams
            grnParams['cancelledby'] = params['current_user']
            grnParams['cancelleddttm'] = params['current_date']
            grnParams['docstatus'] = "C"

            grnSerilIns = grnSeril(
                grnIns, data=grnParams, partial=True)
            if grnSerilIns.is_valid():
                grnSerilIns.save()

            # GRN TABLE DATA AFTER UPDATE
            grnIns = grnSerilIns.data
            vendor_name = Vendor.objects.get(key=grnIns.get("vend_key")).name

            for item in grnItems:

                uomConvunits = Itemuom.objects.get(
                    key=item.get("itemuom_key")).convunits
                stkQty = float(float(item.get("qty")) * float(uomConvunits))

                # Itembatch CHANGES
                if Itembatch.objects.filter(
                    docid=grnIns.get("docid"),
                    doclinekey=item.get("key"),
                    item_key=item.get("item_key"),
                    proj_key=grnIns.get("proj_key"),
                    company_id=grnIns.get("company")
                ).exists():

                    itmBtch = Itembatch.objects.get(
                        docid=grnIns.get("docid"),
                        doclinekey=item.get("key"),
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        company_id=grnIns.get("company")
                    )

                    prevAvlbQty = itmBtch.avlbqty
                    prevTotalAmt = itmBtch.totalamt

                    if float(itmBtch.avlbqty) == stkQty:
                        itmBtch.avlbqty = float(
                            prevAvlbQty) - float(stkQty)
                        itmBtch.totalamt = float(
                            prevTotalAmt) - float(item.get("totalamt"))
                        itmBtch.save()

                    elif float(itmBtch.avlbqty) < stkQty:
                        tmpStockQty = stkQty
                        tmpTotalAmount = float(item.get("totalamt"))

                        pendingQtyToBeRemoved = tmpStockQty - \
                            float(itmBtch.avlbqty)
                        pendingTotlToBeRemoved = tmpTotalAmount - \
                            float(itmBtch.totalamt)

                        itmBtch.avlbqty = 0
                        itmBtch.totalamt = 0
                        itmBtch.save()

                        itmBtchInstnces = Itembatch.objects.filter(
                            docid=grnIns.get("docid"),
                            proj_key=grnIns.get("proj_key"),
                            company_id=grnIns.get("company"),
                            item_key=item.get("item_key")
                        ).exclude(
                            doclinekey=item.get("key"),
                        ).order_by('-createddttm')

                        for otherItemBatches in itmBtchInstnces:

                            prevAvlQty = float(otherItemBatches.avlbqty)
                            prevTtlAmt = float(otherItemBatches.totalamt)

                            if prevAvlQty < pendingQtyToBeRemoved:
                                otherItemBatches.avlbqty = 0
                                otherItemBatches.totalamt = prevTtlAmt - pendingTotlToBeRemoved
                                otherItemBatches.save()

                                pendingQtyToBeRemoved = pendingQtyToBeRemoved - prevAvlQty
                                pendingTotlToBeRemoved = pendingTotlToBeRemoved - prevTtlAmt

                            elif prevAvlQty == pendingQtyToBeRemoved:
                                otherItemBatches.avlbqty = 0
                                otherItemBatches.totalamt = prevTtlAmt - pendingTotlToBeRemoved
                                otherItemBatches.save()
                                break

                            else:
                                otherItemBatches.avlbqty = prevAvlQty - pendingQtyToBeRemoved
                                otherItemBatches.avlbqty = prevTtlAmt - pendingTotlToBeRemoved
                                otherItemBatches.save()
                                break

                    # ItembatchLedger CHANGES
                    # itmBtchLdg = ItembatchLedger(
                    #     docid=grnIns.get("docid"),
                    #     dockey=grnIns.get("key"),
                    #     doclinekey=item.get("key"),
                    #     docdate=grnIns.get("date"),
                    #     item_key=item.get("item_key"),
                    #     itembtch_key=itmBtch.key,
                    #     proj_key=grnIns.get("proj_key"),
                    #     qty=float(stkQty) * -1,
                    #     unitcost=float(item.get("totalamt")) / stkQty,
                    #     totalamt=float(item.get("totalamt")) * -1,
                    #     createdby=params['current_user'],
                    #     createddttm=params['current_date'],
                    #     company_id=grnIns.get("company"),
                    #     client_id=grnIns.get("client_id")
                    # )
                    # itmBtchLdg.save()

                    # StockLedger CHANGES
                    # sLedger = StockLedger(

                    #     docid=grnIns.get("docid"),
                    #     dockey=grnIns.get("key"),
                    #     doclinekey=item.get("key"),
                    #     docnumber=grnIns.get("number"),
                    #     docdate=grnIns.get("date"),
                    #     item_key=item.get("item_key"),
                    #     proj_key=grnIns.get("proj_key"),
                    #     qty=float(stkQty) * -1,
                    #     unitcost=float(item.get("totalamt")) / stkQty,
                    #     totalamt=float(item.get("totalamt")) * -1,
                    #     notes=str(
                    #         vendor_name + "|" + grnIns.get("vendrefno") + "|" + item.get("_itemnotes"))[0:255],
                    #     createdby=params['current_user'],
                    #     createddttm=params['current_date'],
                    #     company_id=grnIns.get("company"),
                    #     client_id=grnIns.get("client_id")
                    # )
                    # sLedger.save()

                    # StockQoh changes update
                    if StockQoh.objects.filter(
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        company_id=grnIns.get("company")
                    ).exists():
                        # StockQoh update
                        stockQohIns = StockQoh.objects.get(
                            item_key=item.get("item_key"),
                            proj_key=grnIns.get("proj_key"),
                            company_id=grnIns.get("company")
                        )

                        prevQty = stockQohIns.qty
                        prevValue = stockQohIns.value

                        stockQohIns.qty = float(
                            prevQty) - float(stkQty)
                        stockQohIns.value = float(
                            prevValue) - float(item.get("totalamt"))
                        stockQohIns.save()

                    # StockSummary changes
                    grnDtObj = datetime.strptime(
                        grnIns.get("date"), '%Y-%m-%d')
                    grnYear = grnDtObj.year
                    grnMonth = grnDtObj.month

                    if StockSummary.objects.filter(
                        year=grnYear,
                        month=grnMonth,
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        company_id=grnIns.get("company")
                    ).exists():
                        # StockSummary insert
                        stcSumyObj = StockSummary.objects.get(
                            year=grnYear,
                            month=grnMonth,
                            item_key=item.get("item_key"),
                            proj_key=grnIns.get("proj_key"),
                            company_id=grnIns.get("company")
                        )
                        prevPurchQty = stcSumyObj.purchqty
                        prevPurchAmt = stcSumyObj.purchamt
                        stcSumyObj.purchqty = float(
                            prevPurchQty) - float(stkQty)
                        stcSumyObj.PurchAmt = float(
                            prevPurchAmt) - float(item.get("totalamt"))
                        stcSumyObj.save()

        else:

            # Material Purchase CHAGES
            grnParams['submittedby'] = params['current_user']
            grnParams['submitteddttm'] = params['current_date']
            grnParams['docstatus'] = "U"

            grnSerilIns = grnSeril(
                grnIns, data=grnParams, partial=True)
            if grnSerilIns.is_valid():
                grnSerilIns.save()

            # GRN TABLE DATA AFTER UPDATE
            grnIns = grnSerilIns.data
            vendor_name = Vendor.objects.get(key=grnIns.get("vend_key")).name

            for item in grnItems:

                uomConvunits = Itemuom.objects.get(
                    key=item.get("itemuom_key")).convunits
                stkQty = float(float(item.get("qty")) * float(uomConvunits))

                # Itembatch CHANGES
                itmBtch = Itembatch(
                    docid=grnIns.get("docid"),
                    dockey=grnIns.get("key"),
                    doclinekey=item.get("key"),
                    docdate=grnIns.get("date"),
                    item_key=item.get("item_key"),
                    proj_key=grnIns.get("proj_key"),
                    rcptqty=stkQty,  # use stockqty
                    avlbqty=stkQty,  # use stockqty
                    unitcost=float(item.get("totalamt")) / \
                    float(stkQty),  # use stockqty
                    totalamt=item.get("totalamt"),
                    company_id=grnIns.get("company"),
                    client_id=grnIns.get("client_id")
                )
                itmBtch.save()

                # ItembatchLedger CHANGES
                irmBtchLdg = ItembatchLedger(
                    docid=grnIns.get("docid"),
                    dockey=grnIns.get("key"),
                    doclinekey=item.get("key"),
                    docdate=grnIns.get("date"),
                    item_key=item.get("item_key"),
                    itembtch_key=itmBtch.key,
                    proj_key=grnIns.get("proj_key"),
                    qty=stkQty,
                    unitcost=float(item.get("totalamt")) /
                    float(stkQty),
                    totalamt=item.get("totalamt"),
                    createdby=params['current_user'],
                    createddttm=params['current_date'],
                    company_id=grnIns.get("company"),
                    client_id=grnIns.get("client_id")
                )
                irmBtchLdg.save()

                # StockLedger CHANGES
                sLedger = StockLedger(
                    docid=grnIns.get("docid"),
                    dockey=grnIns.get("key"),
                    doclinekey=item.get("key"),
                    docnumber=grnIns.get("number"),
                    docdate=grnIns.get("date"),
                    item_key=item.get("item_key"),
                    proj_key=grnIns.get("proj_key"),
                    qty=stkQty,
                    unitcost=float(item.get("totalamt")) /
                    float(stkQty),
                    totalamt=item.get("totalamt"),
                    notes=str(vendor_name + "|" + grnIns.get("vendrefno") +
                              "|" + item.get("_itemnotes"))[0:255],
                    createdby=params['current_user'],
                    createddttm=params['current_date'],
                    company_id=grnIns.get("company"),
                    client_id=grnIns.get("client_id")
                )
                sLedger.save()

                # StockQoh changes update
                if StockQoh.objects.filter(
                    item_key=item.get("item_key"),
                    proj_key=grnIns.get("proj_key"),
                    company_id=grnIns.get("company")
                ).exists():
                    # StockQoh update
                    stockQohIns = StockQoh.objects.get(
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        company_id=grnIns.get("company")
                    )
                    prevQty = stockQohIns.qty
                    prevValue = stockQohIns.value
                    stockQohIns.qty = float(
                        prevQty) + float(stkQty)
                    stockQohIns.value = float(
                        prevValue) + float(item.get("totalamt"))
                    stockQohIns.save()

                else:
                    # StockQoh insert
                    stockQohIns = StockQoh(
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        qty=float(stkQty),
                        value=float(item.get("totalamt")),
                        company_id=grnIns.get("company"),
                        client_id=grnIns.get("client_id")
                    )
                    stockQohIns.save()

                # StockSummary changes
                grnDtObj = datetime.strptime(
                    grnIns.get("date"), '%Y-%m-%d')
                grnYear = grnDtObj.year
                grnMonth = grnDtObj.month

                if StockSummary.objects.filter(
                    year=grnYear,
                    month=grnMonth,
                    item_key=item.get("item_key"),
                    proj_key=grnIns.get("proj_key"),
                    company_id=grnIns.get("company")
                ).exists():
                    # StockSummary insert
                    stcSumyObj = StockSummary.objects.get(
                        year=grnYear,
                        month=grnMonth,
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        company_id=grnIns.get("company")
                    )

                    prevPurchQty = stcSumyObj.purchqty
                    prevPurchAmt = stcSumyObj.purchamt
                    stcSumyObj.purchqty = float(
                        prevPurchQty) + float(stkQty)
                    stcSumyObj.PurchAmt = float(
                        prevPurchAmt) + float(item.get("totalamt"))
                    stcSumyObj.save()
                else:
                    stkSum = StockSummary(
                        year=grnYear,
                        month=grnMonth,
                        item_key=item.get("item_key"),
                        proj_key=grnIns.get("proj_key"),
                        purchqty=float(stkQty),
                        purchamt=float(item.get("totalamt")),
                        company_id=grnIns.get("company"),
                        client_id=grnIns.get("client_id")
                    )
                    stkSum.save()

        return True
        # except:
        #     return False

    def insertGRNItems(self, params, grnSeril):
        grnID = params.get("key", False)
        company = params.get("company", False)
        client_id = params.get("client_id", False)
        user = params.get("user")

        # remove all GRN ITEMS initially
        self.deleteAllGRNItemByGRNID(grnID)

        if grnID and company and client_id:
            insertedData = []
            grnItems = params.get('grn_items', [])
            for item in grnItems:
                item['grn_key'] = grnID
                item['company'] = company
                item['client_id'] = client_id
                item['createdby'] = user
                serializer = grnSeril(data=item)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        return {}, False, "Error in API request", serializer.errors
                except:
                    # if any one GRN items failed to load, delete all GRN items
                    self.deleteAllGRNItemByGRNID(grnID)
                    return {}, False, "Error While Adding GRN items1", {}

            if len(insertedData) == len(grnItems):
                return insertedData, True, "GRN items Modified Successfully", {}
            else:
                # if any one GRN items failed to load, delete all GRN items
                self.deleteAllGRNItemByGRNID(grnID)
                return {}, False, "Error While Adding GRN items", {}
        else:
            return {}, False, "grn_key (or) company (or) client_id is missing", {}

    def deleteAllGRNItemByGRNID(self, grnID):
        GoodsreceiptnoteItems.objects.filter(grn_key=grnID).delete()

    def deleteGRNByGRNID(self, grnID):
        Goodsreceiptnote.objects.get(key=grnID).delete()


class PaymentManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().all()

    def savePayment(self, params, serializer):
        serializerIns = serializer(data=params)
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Payment Added Successfully", {}
            except:
                return {}, False, "Error While Adding Payment", {}

        return {}, False, "Error in API request", serializerIns.errors

    def updateAllocationTable(self, invoice, payment, amount, company, client, user, datetime):
        allocationIns = Paymentalloc(
            pay_key=Payment.objects.get(pk=payment),
            vendinv_key=Vendorinvoice.objects.get(pk=invoice),
            allocamt=amount,
            company=Company.objects.get(pk=company),
            client_id=client,
            createdby=user,
            createddttm=datetime
        )
        allocationIns.save()

    def updateInvoiceTable(self, invoiceKey, balAmt, docStatus):
        singleInvcIns = Vendorinvoice.objects.get(pk=invoiceKey)
        singleInvcIns.balamt = balAmt
        singleInvcIns.docstatus = docStatus
        singleInvcIns.save()

    def updateInvoiceAmountAllocations(self, params, paymentKey, user, datetime):
        amountToBeMinus = float(params["paidamt"])
        vendorKey = float(params["vend_key"])

        vendInvcIns = Vendorinvoice.objects.filter(
            vend_key=vendorKey,
            docstatus__in=["U", "PP"]
        ).order_by('key')

        if vendInvcIns.exists():
            currentInvoiceFlag = 0
            paymentList = []

            while (amountToBeMinus > 0):

                if (currentInvoiceFlag == vendInvcIns.count()):
                    break  # to prevent the index issue

                invoicePendingAmount = float(
                    vendInvcIns[currentInvoiceFlag].balamt)

                if (invoicePendingAmount == amountToBeMinus):
                    print("This Invoice has been paid Fully")
                    invoicePendingAmount = 0
                    amountSpended = amountToBeMinus
                    amountToBeMinus = 0
                    docstatus = "FP"

                elif (invoicePendingAmount > amountToBeMinus):
                    print("This Invoice has been paid Fully")
                    invoicePendingAmount = invoicePendingAmount - amountToBeMinus
                    amountSpended = amountToBeMinus
                    amountToBeMinus = 0
                    docstatus = "PP"

                elif (invoicePendingAmount < amountToBeMinus):
                    print("This Invoice has been paid partially")
                    amountSpended = invoicePendingAmount
                    amountToBeMinus = amountToBeMinus - invoicePendingAmount
                    invoicePendingAmount = 0
                    docstatus = "FP"

                paymentList.append({
                    "vendor_invoice_key": vendInvcIns[currentInvoiceFlag].key,
                    "doc_status": docstatus,
                    "balance_invoice_amount": invoicePendingAmount,
                    "amount_allocated": amountSpended,
                    "payment_key": paymentKey,
                    "company": params["company"],
                    "client_id": params["client_id"],
                    "user": user,
                    "datetime": datetime
                })

                currentInvoiceFlag = currentInvoiceFlag + 1

            print(paymentList)

            fullyPaidCounter = 0
            for pay in paymentList:

                # First update invoice table
                self.updateInvoiceTable(
                    pay.get("vendor_invoice_key"),
                    pay.get("balance_invoice_amount"),
                    pay.get("doc_status")
                )

                # second update amount allocation table
                self.updateAllocationTable(
                    pay.get("vendor_invoice_key"),
                    pay.get("payment_key"),
                    pay.get("amount_allocated"),
                    pay.get("company"),
                    pay.get("client_id"),
                    pay.get("user"),
                    pay.get("datetime")
                )

                if pay.get("doc_status") == "FP":
                    fullyPaidCounter += 1

            if fullyPaidCounter == len(paymentList):
                print("ALL INVOICE PAID")
            else:
                print("NOT ALL INVOICES PAIND")

    def updatePayment(self, params, serializer, payKey, additionalParams={}):
        payIns = get_object_or_404(self.get_queryset(), pk=payKey)
        try:
            serializerIns = serializer(payIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    return serializerIns.data, True, "Payment Updated Successfully", {}
                except:
                    return {}, False, "Error In Payment PUT Request", {}
            else:
                return {}, False, "Error In Payment PUT Request", serializerIns.errors
        except Exception as e:
            return {}, False, e.message, {}

    def submitPayment(self, params, serializer, payKey, additionalParams={},):
        payIns = get_object_or_404(self.get_queryset(), pk=payKey)
        try:
            serializerIns = serializer(payIns, data=params, partial=True)
            if serializerIns.is_valid():
                try:
                    serializerIns.save()
                    # update balance amount of vendor payment
                    self.updateInvoiceAmountAllocations(
                        params,
                        serializerIns.data.get("key"),
                        additionalParams.get("user"),
                        additionalParams.get("datetime")
                    )
                    return serializerIns.data, True, "Payment Updated Successfully", {}
                except:
                    return {}, False, "Error In Payment Post Request", {}
            else:
                return {}, False, "Error In Payment Post Request", serializerIns.errors
        except Exception as e:
            return {}, False, e.message, {}

    def revortInvoiceAmount(self, invoice, invoiceAmt):
        totalPending = invoice.balamt
        ovrallamount = invoice.invamt

        newAmountToUpdate = totalPending + invoiceAmt

        if newAmountToUpdate == ovrallamount:
            docstatus = "U"
        else:
            docstatus = "PP"

        invoice.balamt = newAmountToUpdate
        invoice.docstatus = docstatus
        invoice.save()

    def cancelPayment(self, payKey, serializer):
        payIns = get_object_or_404(self.get_queryset(), pk=payKey)

        paymentAlloIns = Paymentalloc.objects.filter(pay_key=payKey)

        for alloc in paymentAlloIns:
            invoice = alloc.vendinv_key
            invoiceAmt = alloc.allocamt

            self.revortInvoiceAmount(invoice, invoiceAmt)

        serializerIns = serializer(
            payIns,
            data={"docstatus": "C"},
            partial=True
        )
        if serializerIns.is_valid():
            try:
                serializerIns.save()
                return serializerIns.data, True, "Payment Cancelled Successfully", {}
            except:
                return {}, False, "Error In Payment Cancel Request", {}
        return {}, False, "Error In Payment Cancel Request", serializerIns.errors


class Docid(models.Model):
    key = models.AutoField(db_column='DocKey', primary_key=True)
    docid = models.CharField(db_column='DocID',max_length=5)
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,db_column="DocID_ClientID")
    docname = models.CharField(db_column='DocName', max_length=50)
    docnumber = models.IntegerField(db_column='DocNumber')

    class Meta:
        managed = True
        db_table = 'DocID'


class Docstatus(models.Model):
    docstatus = models.CharField(
        db_column='DocStatus', primary_key=True, max_length=2)
    descr = models.CharField(
        db_column='DocStatus_Descr', max_length=50)

    class Meta:
        managed = True
        db_table = 'DocStatus'


class Goodsreceiptnote(models.Model):
    key = models.AutoField(db_column='GRN_Key', primary_key=True)
    docid = models.CharField(db_column='GRN_DocID', max_length=3)
    number = models.CharField(db_column='GRN_Number', max_length=25)
    date = models.DateField(db_column='GRN_Date')
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='GRN_Vend_Key')
    vendrefno = models.CharField(
        db_column='GRN_VendRefNo', max_length=25, blank=True, null=True)
    pono = models.CharField(db_column='GRN_PONo',
                            max_length=25, blank=True, null=True)
    loctyp = models.CharField(db_column='GRN_LocTyp', max_length=2)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='GRN_Proj_Key', blank=True, null=True)
    wh_key = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, db_column='GRN_WH_Key', blank=True, null=True)
    driver = models.CharField(db_column='GRN_Driver',
                              max_length=25, blank=True, null=True)
    vehicle = models.CharField(
        db_column='GRN_Vehicle', max_length=25, blank=True, null=True)
    docstatus = models.CharField(
        db_column='GRN_DocStatus', max_length=2, blank=True, null=True)
    submitteddttm = models.DateTimeField(
        db_column='GRN_SubmittedDtTm', blank=True, null=True)
    submittedby = models.CharField(
        db_column='GRN_SubmittedBy', max_length=100, blank=True, null=True)
    vendinv_key = models.IntegerField(
        db_column='GRN_VendInv_Key', blank=True, null=True)
    cancelleddttm = models.DateTimeField(
        db_column='GRN_CancelledDtTm', blank=True, null=True)
    cancelledby = models.CharField(
        db_column='GRN_CancelledBy', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='GRN_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='GRN_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='GRN_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='GRN_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='GRN_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='GRN_Client_ID')
    objects = GRNManager()

    class Meta:
        managed = True
        db_table = 'GoodsReceiptNote'
        unique_together = (('company', 'docid', 'number'),)


class GoodsreceiptnoteItems(models.Model):
    key = models.AutoField(db_column='GRNItm_Key', primary_key=True)
    grn_key = models.ForeignKey(
        Goodsreceiptnote, on_delete=models.CASCADE, db_column='GRNItm_GRN_Key')
    item_key = models.ForeignKey(
        Item, models.CASCADE, db_column='GRNItm_Item_Key')
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='GRNItm_ItemUOM_Key')
    qty = models.DecimalField(
        db_column='GRNItm_Qty', max_digits=15, decimal_places=5, blank=True, null=True)
    _itemnotes = models.CharField(
        db_column='GRNItem_ItemNotes', max_length=255, blank=True, null=True)
    unitprice = models.DecimalField(
        db_column='GRNItm_UnitPrice', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='GRNItm_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    taxamt = models.DecimalField(
        db_column='GRNItm_TaxAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    totalamt = models.DecimalField(
        db_column='GRNItm_TotalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='GRNItm_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='GRNItm_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='GRNItm_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='GRNItm_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='GRNItm_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='GRNItm_Client_ID')

    class Meta:
        managed = True
        db_table = 'GoodsReceiptNote_Items'
        unique_together = (('company', 'grn_key', 'item_key', 'itemuom_key'),)


class StockLedger(models.Model):
    key = models.AutoField(db_column='StkLdgr_Key', primary_key=True)
    docid = models.CharField(db_column='StkLdgr_DocID', max_length=3)
    dockey = models.IntegerField(db_column='StkLdgr_DocKey')
    doclinekey = models.IntegerField(db_column='StkLdgr_DocLineKey')
    docnumber = models.CharField(db_column='StkLdgr_DocNumber', max_length=25)
    docdate = models.DateField(db_column='StkLdgr_DocDate')
    item_key = models.IntegerField(db_column='StkLdgr_Item_Key')
    wh_key = models.IntegerField(
        db_column='StkLdgr_WH_Key', blank=True, null=True)
    proj_key = models.IntegerField(
        db_column='StkLdgr_Proj_Key', blank=True, null=True)
    qty = models.DecimalField(
        db_column='StkLdgr_Qty', max_digits=15, decimal_places=5, blank=True, null=True)
    unitcost = models.DecimalField(
        db_column='StkLdgr_UnitCost', max_digits=15, decimal_places=5, blank=True, null=True)
    totalamt = models.DecimalField(
        db_column='StkLdgr_TotalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    notes = models.CharField(db_column='StkLdgr_Notes',
                             max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='StkLdgr_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='StkLdgr_CreatedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE,
                                   db_column='StkLdgr_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='StkLdgr_Client_ID')

    class Meta:
        managed = True
        db_table = 'Stock_Ledger'
        unique_together = (('company_id', 'dockey', 'doclinekey'),)


class StockQoh(models.Model):
    key = models.AutoField(db_column='StkQOH_Key', primary_key=True)
    item_key = models.IntegerField(db_column='StkQOH_Item_Key')
    wh_key = models.IntegerField(
        db_column='StkQOH_WH_Key', blank=True, null=True)
    proj_key = models.IntegerField(
        db_column='StkQOH_Proj_Key', blank=True, null=True)
    qty = models.DecimalField(
        db_column='StkQOH_Qty', max_digits=15, decimal_places=5, blank=True, null=True)
    value = models.DecimalField(
        db_column='StkQOH_Value', max_digits=15, decimal_places=2, blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='StkQOH_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='StkQOH_Client_ID')

    class Meta:
        managed = True
        db_table = 'Stock_QOH'
        unique_together = (('company_id', 'item_key', 'proj_key'),
                           ('company_id', 'item_key', 'wh_key'),)


class StockSummary(models.Model):
    key = models.AutoField(db_column='StkSum_Key', primary_key=True)
    year = models.IntegerField(db_column='StkSum_Year')
    month = models.IntegerField(db_column='StkSum_Month')
    item_key = models.IntegerField(db_column='StkSum_Item_Key')
    wh_key = models.IntegerField(
        db_column='StkSum_WH_Key', blank=True, null=True)
    proj_key = models.IntegerField(
        db_column='StkSum_Proj_Key', blank=True, null=True)
    beginbalqty = models.DecimalField(
        db_column='StkSum_BeginBalQty', max_digits=15, decimal_places=5, blank=True, null=True)
    beginbalamt = models.DecimalField(
        db_column='StkSum_BeginBalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    purchqty = models.DecimalField(
        db_column='StkSum_PurchQty', max_digits=15, decimal_places=5, blank=True, null=True)
    purchamt = models.DecimalField(
        db_column='StkSum_PurchAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    consumeqty = models.DecimalField(
        db_column='StkSum_ConsumeQty', max_digits=15, decimal_places=5, blank=True, null=True)
    consumeamt = models.DecimalField(
        db_column='StkSum_ConsumeAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    trfinqty = models.DecimalField(
        db_column='StkSum_TrfInQty', max_digits=15, decimal_places=5, blank=True, null=True)
    trfinamt = models.DecimalField(
        db_column='StkSum_TrfInAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    trfoutqty = models.DecimalField(
        db_column='StkSum_TrfOutQty', max_digits=15, decimal_places=5, blank=True, null=True)
    trfoutamt = models.DecimalField(
        db_column='StkSum_TrfOutAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    adjustqty = models.DecimalField(
        db_column='StkSum_AdjustQty', max_digits=15, decimal_places=5, blank=True, null=True)
    adjustamt = models.DecimalField(
        db_column='StkSum_AdjustAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='StkSum_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='StkSum_Client_ID')

    class Meta:
        managed = True
        db_table = 'Stock_Summary'
        unique_together = (('company_id', 'year', 'month', 'item_key', 'proj_key'),
                           ('company_id', 'year', 'month', 'item_key', 'wh_key'),)


class Itembatch(models.Model):
    key = models.AutoField(db_column='ItemBtch_Key', primary_key=True)
    docid = models.CharField(db_column='ItemBtch_DocID', max_length=3)
    dockey = models.IntegerField(db_column='ItemBtch_DocKey')
    doclinekey = models.IntegerField(db_column='ItemBtch_DocLineKey')
    docdate = models.DateField(db_column='ItemBtch_DocDate')
    item_key = models.IntegerField(db_column='ItemBtch_Item_Key')
    wh_key = models.IntegerField(
        db_column='ItemBtch_WH_Key', blank=True, null=True)
    proj_key = models.IntegerField(
        db_column='ItemBtch_Proj_Key', blank=True, null=True)
    rcptqty = models.DecimalField(
        db_column='ItemBtch_RcptQty', max_digits=15, decimal_places=5, blank=True, null=True)
    avlbqty = models.DecimalField(
        db_column='ItemBtch_AvlbQty', max_digits=15, decimal_places=5, blank=True, null=True)
    unitcost = models.DecimalField(
        db_column='ItemBtch_UnitCost', max_digits=15, decimal_places=5, blank=True, null=True)
    totalamt = models.DecimalField(
        db_column='ItemBtch_TotalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='ItemBtch_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItemBtch_CreatedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE,
                                   db_column='ItemBtch_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='ItemBtch_Client_ID')

    class Meta:
        managed = True
        db_table = 'ItemBatch'
        unique_together = (('company_id', 'dockey', 'doclinekey'),)


class ItembatchLedger(models.Model):
    key = models.AutoField(db_column='ItmBtchLdgr_Key', primary_key=True)
    docid = models.CharField(db_column='ItmBtchLdgr_DocID', max_length=3)
    dockey = models.IntegerField(db_column='ItmBtchLdgr_DocKey')
    doclinekey = models.IntegerField(db_column='ItmBtchLdgr_DocLineKey')
    docdate = models.DateField(db_column='ItmBtchLdgr_DocDate')
    item_key = models.IntegerField(db_column='ItmBtchLdgr_Item_Key')
    itembtch_key = models.IntegerField(db_column='ItmBtchLdgr_ItemBtch_Key')
    wh_key = models.IntegerField(
        db_column='ItmBtchLdgr_WH_Key', blank=True, null=True)
    proj_key = models.IntegerField(
        db_column='ItmBtchLdgr_Proj_Key', blank=True, null=True)
    qty = models.DecimalField(db_column='ItmBtchLdgr_Qty',
                              max_digits=15, decimal_places=5, blank=True, null=True)
    unitcost = models.DecimalField(
        db_column='ItmBtchLdgr_UnitCost', max_digits=15, decimal_places=5, blank=True, null=True)
    totalamt = models.DecimalField(
        db_column='ItmBtchLdgr_TotalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='ItmBtchLdgr_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='ItmBtchLdgr_CreatedDtTm', blank=True, null=True)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE,
                                   db_column='ItmBtchLdgr_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='ItmBtchLdgr_Client_ID')

    class Meta:
        managed = True
        db_table = 'ItemBatch_Ledger'
        unique_together = (
            ('company_id', 'dockey', 'doclinekey', 'itembtch_key'),)


class Purchasetemplate(models.Model):
    key = models.AutoField(db_column='PurTmpl_Key', primary_key=True)
    docid = models.CharField(db_column='PurTmpl_DocID', max_length=3)
    number = models.CharField(db_column='PurTmpl_Number', max_length=25)
    name = models.CharField(db_column='PurTmpl_Name', max_length=50)
    inactive = models.CharField(db_column='PurTmpl_InActive', max_length=1)
    createdby = models.CharField(
        db_column='PurTmpl_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='PurTmpl_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='PurTmpl_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='PurTmpl_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='PurTmpl_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='PurTmpl_Client_ID')
    itemtyp_key = models.ForeignKey(
        Itemtype, on_delete=models.CASCADE, db_column='PurTmpl_ItemTyp_Key')

    class Meta:
        managed = True
        db_table = 'PurchaseTemplate'
        unique_together = (('company', 'docid', 'number'),)


class PurchasetemplateItems(models.Model):
    key = models.AutoField(db_column='PurTmplItm_Key', primary_key=True)
    purtmpl_key = models.ForeignKey(
        Purchasetemplate, on_delete=models.CASCADE, db_column='PurTmplItm_PurTmpl_Key')
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='PurTmplItm_Item_Key')
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='PurTmplItm_ItemUOM_Key')
    itemnotes = models.CharField(
        db_column='PurTmplItm_ItemNotes', max_length=255, blank=True, null=True)
    createdby = models.CharField(
        db_column='PurTmplItm_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='PurTmplItm_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='PurTmplItm_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='PurTmplItm_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='PurTmplItm_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='PurTmplItm_Client_ID')

    class Meta:
        managed = True
        db_table = 'PurchaseTemplate_Items'
        unique_together = (
            ('company', 'purtmpl_key', 'item_key', 'itemuom_key'),)


class Purchaseorder(models.Model):
    key = models.AutoField(db_column='PO_Key', primary_key=True)
    number = models.CharField(db_column='PO_Number', max_length=25)
    date = models.DateField(db_column='PO_Date')
    desc = models.CharField(
        db_column='PO_Desc', max_length=255, blank=True, null=True)
    status = models.CharField(
        db_column='PO_Status', max_length=2, default="O")
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='PO_Vend_Key', blank=True, null=True)
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='PO_Proj_Key', blank=True, null=True)
    item_type_key = models.ForeignKey(Itemtype, on_delete=models.CASCADE, db_column='PO_ItemType_Key', blank=True, null=True)
    netamt = models.DecimalField(
        db_column='PO_NetAmt', max_digits=15, decimal_places=2, default=0)
    createdby = models.CharField(
        db_column='PO_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='PO_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='PO_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='PO_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='PO_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='PO_Client_ID')

    class Meta:
        managed = True
        db_table = 'PurchaseOrder'
        unique_together = (('company', 'number'),)


class PurchaseorderItems(models.Model):
    key = models.AutoField(db_column='POItm_Key', primary_key=True)
    po_key = models.ForeignKey(
        Purchaseorder, on_delete=models.CASCADE, db_column='POItm_PO_Key')
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='POItm_Item_Key')
    item_uom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='POItm_ItemUom_Key', blank=True, null=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, db_column='POItm_Brand', blank=True, null=True)
    model_number = models.CharField(
        db_column='POItm_ModelNumber', max_length=255, blank=True, null=True)
    qty = models.DecimalField(
        db_column='POItm_Qty', max_digits=15, decimal_places=5, blank=True, null=True)
    unit = models.DecimalField(
        db_column='POItm_Unit', max_digits=15, decimal_places=5, blank=True, null=True)
    gst = models.IntegerField(
        db_column='POItm_GSTPercent', blank=True, null=True)
    gstamt = models.DecimalField(
        db_column='POItm_GSTAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='POItm_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='POItm_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='POItm_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='POItm_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='POItm_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='POItm_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='POItm_Client_ID')

    class Meta:
        managed = True
        db_table = 'PurchaseOrder_Items'


class Vendorinvoice(models.Model):
    key = models.AutoField(db_column='VendInv_Key', primary_key=True)
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='VendInv_Vend_Key')
    proj_key = models.ForeignKey(
        Project, on_delete=models.CASCADE, db_column='VendInv_Proj_Key', blank=True, null=True)
    invoiceno = models.CharField(db_column='VendInv_InvoiceNo', max_length=25)
    vendor_invoice_no = models.CharField(db_column='VendInv_VendInvoiceNo', max_length=100, null=True, blank=True)
    invoicedate = models.DateField(db_column='VendInv_InvoiceDate')
    invnotes = models.TextField(
        db_column='VendInv_InvNotes',max_length=500, blank=True, null=True)
    method = models.CharField(db_column='VendInv_Method', max_length=25, default='direct')
    po_key = models.ForeignKey( 
        Purchaseorder, on_delete=models.CASCADE, db_column='VendInv_PO_Key', blank=True, null=True)
    invamt = models.DecimalField(
        db_column='VendInv_InvAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='VendInv_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, db_column="VendorInv_PaidAmount")
    balamt = models.DecimalField(
        db_column='VendInv_BalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    tdsamt = models.DecimalField(
        db_column='VendInv_TdsAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    gstamt = models.DecimalField(
        db_column='VendInv_GstAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    transport_chrgs = models.DecimalField(
        db_column='VendInv_TransportChrgs', max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    handling_chrgs = models.DecimalField(
        db_column='VendInv_HandlingChrgs', max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    discountamt = models.DecimalField(
        db_column='VendInv_DiscountAmt', max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    roundedamt = models.DecimalField(
        db_column='VendInv_RoundedAmt', max_digits=15, decimal_places=3, default=0, blank=True, null=True)
    rounded_action_choices = [('A', 'A'), ('S', 'S')]
    rounded_action = models.CharField(
        max_length=10, choices=rounded_action_choices, db_column='VendInv_RoundedAction', blank=True, null=True)
    invoice_status_choices = [('O', 'O'), ('P', 'P'), ('A', 'A')]
    invoice_status = models.CharField(
        max_length=1, choices=invoice_status_choices, db_column="VendorInv_InvoiceStatus", default="O")
    createdby = models.CharField(
        db_column='VendInv_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendInv_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendInv_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendInv_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendInv_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='VendInv_Client_ID')

    class Meta:
        managed = True
        db_table = 'VendorInvoice'
        unique_together = (('company', 'invoiceno'),)


class VendorInvoiceImage(models.Model):
    key = models.AutoField(db_column='VendInvImg_Key', primary_key=True)
    vendor_invoice = models.ForeignKey(
        Vendorinvoice,
        related_name="invoice_images",
        on_delete=models.CASCADE,
        db_column='VendInvImg_Inv_Key'
    )
    image_url = models.TextField(db_column="VendInvImg_URL")
    client_id = models.IntegerField(db_column="VendInvImg_Client_ID")
    company_id = models.IntegerField(db_column="VendInvImg_Company_ID")
    createdby = models.CharField(
        db_column='VendInvImg_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(db_column='VendInvImg_CreatedDtTm', auto_now_add=True)
    lastmodifiedby = models.CharField(
        db_column='VendInvImg_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendInvImg_LastModifiedDtTm', blank=True, null=True)

    class Meta:
        db_table = "VendorInvoice_Images"


class VendorinvoiceItems(models.Model):
    key = models.AutoField(db_column='VendInvItm_Key', primary_key=True)
    vendinv_key = models.ForeignKey(
        Vendorinvoice, on_delete=models.CASCADE, db_column='VendInvItm_VendInv_Key')
    item_key = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column='VendInvItm_Item_Key', blank=True, null=True)
    item_descr = models.CharField(
        db_column='VendInvItm_Item_Descr', max_length=100, blank=True, null=True)
    grnitm_key = models.IntegerField(
        db_column='VendInvItm_GRNItm_Key', blank=True, null=True)
    itemuom_key = models.ForeignKey(
        Itemuom, on_delete=models.CASCADE, db_column='VendInvItm_ItemUOM_Key')
    qty = models.DecimalField(db_column='VendInvItm_Qty',
                              max_digits=15, decimal_places=5, blank=True, null=True)
    mnotes = models.CharField(
        db_column='GRNItem_ItemNotes', max_length=255, blank=True, null=True)
    unitprice = models.DecimalField(
        db_column='VendInvItm_UnitPrice', max_digits=15, decimal_places=2, blank=True, null=True)
    netamt = models.DecimalField(
        db_column='VendInvItm_NetAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    taxamt = models.DecimalField(
        db_column='VendInvItm_TaxAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    totalamt = models.DecimalField(
        db_column='VendInvItm_TotalAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendInvItm_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendInvItm_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='VendInvItm_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='VendInvItm_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='VendInvItm_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='VendInvItm_Client_ID')

    class Meta:
        managed = True
        db_table = 'VendorInvoice_Items'
        unique_together = (
            ('company', 'vendinv_key', 'item_key', 'itemuom_key'),)


class VendorLedger(models.Model):
    key = models.AutoField(db_column='VendLdgr_Key', primary_key=True)
    vend_key = models.IntegerField(db_column='VendLdgr_Vend_Key')
    docid = models.CharField(db_column='VendLdgr_DocID', max_length=3)
    dockey = models.IntegerField(db_column='VendLdgr_DocKey')
    doclinekey = models.IntegerField(db_column='VendLdgr_DocLineKey')
    docnumber = models.CharField(db_column='VendLdgr_DocNumber', max_length=25)
    docdate = models.DateField(db_column='VendLdgr_DocDate')
    notes = models.CharField(db_column='VendLdgr_Notes',
                             max_length=255, blank=True, null=True)
    amt = models.DecimalField(
        db_column='VendLdgr_Amt', max_digits=15, decimal_places=2, blank=True, null=True)
    createdby = models.CharField(
        db_column='VendLdgr_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='VendLdgr_CreatedDtTm', blank=True, null=True)
    company_id = models.CharField(
        db_column='VendLdgr_Company_ID', max_length=10)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='VendLdgr_Client_ID')

    class Meta:
        managed = True
        db_table = 'Vendor_Ledger'
        unique_together = (('company_id', 'dockey', 'doclinekey'),)


class Modeofpay(models.Model):
    modeofpay = models.CharField(
        db_column='ModeOfPay', primary_key=True, max_length=10)
    descr = models.CharField(db_column='ModeOfPay_Descr', max_length=50)

    class Meta:
        managed = True
        db_table = 'ModeOfPay'


class Payment(models.Model):
    key = models.AutoField(db_column='Pay_Key', primary_key=True)
    docid = models.CharField(db_column='Pay_DocID', max_length=3)
    number = models.CharField(db_column='Pay_Number', max_length=25)
    date = models.DateField(db_column='Pay_Date')
    vend_key = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, db_column='Pay_Vend_Key')
    refnumber = models.CharField(
        db_column='Pay_RefNumber', max_length=25, blank=True, null=True)
    modeofpay = models.CharField(db_column='Pay_ModeOfPay', max_length=10)
    bankname = models.CharField(
        db_column='Pay_BankName', max_length=25, blank=True, null=True)
    paidamt = models.DecimalField(
        db_column='Pay_PaidAmt', max_digits=15, decimal_places=2)
    chqno = models.CharField(db_column='Pay_ChqNo',
                             max_length=25, blank=True, null=True)
    chqdate = models.DateField(db_column='Pay_ChqDate', blank=True, null=True)
    chqstatus = models.CharField(
        db_column='Pay_ChqStatus', max_length=2, blank=True, null=True)
    notes = models.CharField(db_column='Pay_Notes',
                             max_length=255, blank=True, null=True)
    docstatus = models.CharField(
        db_column='Pay_DocStatus', max_length=2, blank=True, null=True)
    allocatedamt = models.DecimalField(
        db_column='Pay_AllocatedAmt', max_digits=15, decimal_places=2, blank=True, null=True)
    submitteddttm = models.DateTimeField(
        db_column='Pay_SubmittedDtTm', blank=True, null=True)
    submittedby = models.CharField(
        db_column='Pay_SubmittedBy', max_length=100, blank=True, null=True)
    cancelleddttm = models.DateTimeField(
        db_column='Pay_CancelledDtTm', blank=True, null=True)
    cancelledby = models.CharField(
        db_column='Pay_CancelledBy', max_length=100, blank=True, null=True)
    createdby = models.CharField(
        db_column='Pay_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Pay_CreatedDtTm', blank=True, null=True)
    lastmodifiedby = models.CharField(
        db_column='Pay_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Pay_LastModifiedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='Pay_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='Pay_Client_ID')
    objects = PaymentManager()

    class Meta:
        managed = True
        db_table = 'Payment'
        unique_together = (('company', 'docid', 'number'),)


class Paymentalloc(models.Model):
    key = models.AutoField(db_column='PayAlloc_Key', primary_key=True)
    pay_key = models.ForeignKey(
        Payment, on_delete=models.CASCADE, db_column='PayAlloc_Pay_Key')
    vendinv_key = models.ForeignKey(
        Vendorinvoice, on_delete=models.CASCADE, db_column='PayAlloc_VendInv_Key')
    allocamt = models.DecimalField(
        db_column='PayAlloc_AllocAmt', max_digits=15, decimal_places=2)
    createdby = models.CharField(
        db_column='PayAlloc_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='PayAlloc_CreatedDtTm', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='PayAlloc_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='PayAlloc_Client_ID')

    class Meta:
        managed = True
        db_table = 'PaymentAlloc'
        unique_together = (('pay_key', 'vendinv_key'),)
