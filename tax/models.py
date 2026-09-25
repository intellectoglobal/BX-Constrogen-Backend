from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError


class TdsEntry(models.Model):
    INVOICE_TYPES = [
        ('C', 'Contractor'),
        ('V', 'Vendor'),
    ]
    PAYMENT_STATUSES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    key = models.AutoField(primary_key=True, db_column="TDS_Entry_Key")
    date = models.DateField(db_column="TDS_Entry_Date")
    contractor_invoice = models.ForeignKey(
        'contractor.ContractorInvoice',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="TDS_Entry_ContractorInvoiceID",
        related_name='tds_entries'
    )
    vendor_invoice = models.ForeignKey(
        'pricing.VendorInvoice',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="TDS_Entry_VendorInvoiceID",
        related_name='tds_entries'
    )
    invoice_type = models.CharField(
        max_length=1,
        choices=INVOICE_TYPES,
        db_column="TDS_Entry_InvoiceType"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="TDS_Entry_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_status = models.CharField(
        max_length=6,
        choices=PAYMENT_STATUSES,
        db_column="TDS_Entry_PaymentStatus"
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="TDS_Entry_ClientID",
        related_name='tds_entries'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="TDS_Entry_CompanyID",
        related_name='tds_entries'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="TDS_Entry_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="TDS_Entry_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "TdsEntries"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"TDS Entry {self.key}- {self.date}"

    def clean(self):
        if self.invoice_type == 'C':
            if not self.contractor_invoice:
                raise ValidationError(
                    "Contractor invoice is required for contractor type entries.")
            if self.vendor_invoice:
                raise ValidationError(
                    "Vendor invoice should not be set for contractor type entries.")
        elif self.invoice_type == 'V':
            if not self.vendor_invoice:
                raise ValidationError(
                    "Vendor invoice is required for vendor type entries.")
            if self.contractor_invoice:
                raise ValidationError(
                    "Contractor invoice should not be set for vendor type entries.")
        else:
            raise ValidationError("Invalid invoice type.")


class TdsReport(models.Model):
    ENTITY_TYPES = [
        ('V', 'Vendor'),
        ('C', 'Contractor'),
    ]
    PAYMENT_STATUSES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    key = models.AutoField(primary_key=True, db_column="TDS_Report_Key")
    date = models.DateField(db_column="TDS_Report_Date")
    vendor = models.ForeignKey(
        "vendor.Vendor",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="TDS_Report_VendKey",
        related_name='tds_reports'
    )
    contractor = models.ForeignKey(
        "contractor.Contractor",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="TDS_Report_ContractorKey",
        related_name='tds_reports'
    )
    entity_type = models.CharField(
        max_length=1,
        choices=ENTITY_TYPES,
        db_column="TDS_Report_EntityType"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="TDS_Report_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_status = models.CharField(
        max_length=6,
        choices=PAYMENT_STATUSES,
        db_column="TDS_Report_PaymentStatus"
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="TDS_Report_ClientID",
        related_name='tds_reports'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="TDS_Report_CompanyID",
        related_name='tds_reports'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="TDS_Report_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="TDS_Report_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "TdsReport"
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        if self.entity_type == 'V' and self.vendor:
            name = self.vendor.name
        elif self.entity_type == 'C' and self.contractor:
            name = self.contractor.name
        else:
            name = 'Unknown'
        return f"TDS Report {self.key}- {name}"

    def clean(self):
        if self.entity_type == 'C':
            if not self.contractor:
                raise ValidationError(
                    "Contractor must be set when entity_type is 'Contractor'.")
            if self.vendor:
                raise ValidationError(
                    "Vendor should not be set when entity_type is 'Contractor'.")
        elif self.entity_type == 'V':
            if not self.vendor:
                raise ValidationError(
                    "Vendor must be set when entity_type is 'Vendor'.")
            if self.contractor:
                raise ValidationError(
                    "Contractor should not be set when entity_type is 'Vendor'.")
        else:
            raise ValidationError("Invalid entity type.")

class SalesTds(models.Model):
    PAYMENT_STATUSES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    key = models.AutoField(primary_key=True, db_column="Sales_TDS_Key")
    date = models.DateField(db_column="Sales_TDS_Date")
    project = models.ForeignKey(
        "project.project",
        on_delete=models.CASCADE,
        db_column="Sales_TDS_ProjectID")
    unit = models.ForeignKey(
        "project.Projectunit",
        on_delete=models.CASCADE, 
        db_column="Sales_TDS_UnitID")
    customer = models.ForeignKey(
        "sale.Customer",
        on_delete=models.CASCADE,
        db_column="Sales_TDS_CustKey"
    )
    invoice = models.ForeignKey(
        'sale.SaleInvoice',
        on_delete=models.CASCADE,
        db_column='Sales_TDS_InvoiceID'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Sales_TDS_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_status = models.CharField(
        max_length=6,
        choices=PAYMENT_STATUSES,
        db_column="Sales_TDS_PaymentStatus"
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Sales_TDS_ClientID",
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Sales_TDS_CompanyID",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Sales_TDS_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Sales_TDS_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "SalesTds"
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]


class PurchaseGstEntry(models.Model):
    key = models.AutoField(primary_key=True, db_column="Purch_GST_Entry_Key")
    date = models.DateField(db_column="Purch_GST_Entry_Date")
    vendor = models.ForeignKey(
        "vendor.Vendor",
        on_delete=models.CASCADE,
        db_column="Purch_GST_Entry_VendKey",
        related_name='purchase_gst_entries'
    )
    invoice = models.ForeignKey(
        'pricing.VendorInvoice',
        on_delete=models.CASCADE,
        db_column='Purch_GST_Entry_InvoiceID',
        related_name='purchase_gst_entries'
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Purch_GST_Entry_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Purch_GST_Entry_ClientID",
        related_name='purchase_gst_entries'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Purch_GST_Entry_CompanyID",
        related_name='purchase_gst_entries'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Purch_GST_Entry_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Purch_GST_Entry_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "PurchaseGSTEntry"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"Purchase GST Entry {self.key}- {self.date}"


class PurchaseGstReport(models.Model):
    key = models.AutoField(primary_key=True, db_column="Purch_GST_Report_Key")
    date = models.DateField(db_column="Purch_GST_Report_Date")
    vendor = models.ForeignKey(
        "vendor.Vendor",
        on_delete=models.CASCADE,
        db_column="Purch_GST_Report_VendKey",
        related_name='purchase_gst_reports'
    )
    gst_no = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        db_column="Purch_GST_Report_GSTNo"
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Purch_GST_Report_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Purch_GST_Report_ClientID",
        related_name='purchase_gst_reports'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Purch_GST_Report_CompanyID",
        related_name='purchase_gst_reports'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Purch_GST_Report_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Purch_GST_Report_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "PurchaseGSTReport"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['gst_no']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"Purchase GST Report {self.key}- {self.date}"


class SalesGstEntry(models.Model):
    key = models.AutoField(primary_key=True, db_column="Sales_GST_Entry_Key")
    date = models.DateField(db_column="Sales_GST_Entry_Date")
    project = models.ForeignKey(
        "project.project",
        on_delete=models.CASCADE,
        db_column="Sales_GST_Entry_ProjectID")
    unit = models.ForeignKey(
        "project.Projectunit",
        on_delete=models.CASCADE, 
        db_column="Sales_GST_Entry_UnitID")
    customer = models.ForeignKey(
        "sale.Customer",
        on_delete=models.CASCADE,
        db_column="Sales_GST_Entry_CustKey",
        related_name='sales_gst_entries'
    )
    invoice = models.ForeignKey(
        'sale.SaleInvoice',
        on_delete=models.CASCADE,
        db_column='Sales_GST_Entry_InvoiceID',
        related_name='sale_gst_entries'
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Sales_GST_Entry_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Sales_GST_Entry_ClientID",
        related_name='sales_gst_entries'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Sales_GST_Entry_CompanyID",
        related_name='sales_gst_entries'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Sales_GST_Entry_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Sales_GST_Entry_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "SalesGSTEntry"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"Sales GST Entry {self.key}- {self.date}"


class SalesGstReport(models.Model):
    key = models.AutoField(primary_key=True, db_column="Sales_GST_Report_Key")
    date = models.DateField(db_column="Sales_GST_Report_Date")
    customer = models.ForeignKey(
        "sale.Customer",
        on_delete=models.CASCADE,
        db_column="Sales_GST_Report_CustKey",
        related_name='sales_gst_reports'
    )
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE, 
        db_column="Sales_GST_Report_ProjectID")
    unit = models.ForeignKey(
        "project.Projectunit",
        on_delete=models.CASCADE, 
        db_column="Sales_GST_Report_UnitID")
    agreement = models.ForeignKey(
        'sale.SaleAgreement',
        on_delete=models.CASCADE,
        db_column='Sales_GST_Entry_AgreementID',
        related_name='sale_gst_entries'
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Sales_GST_Report_Amount",
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    client = models.ForeignKey(
        'client.ClientBase',
        on_delete=models.CASCADE,
        db_column="Sales_GST_Report_ClientID",
        related_name='sales_gst_reports'
    )
    company = models.ForeignKey(
        'client.Company',
        on_delete=models.CASCADE,
        db_column="Sales_GST_Report_CompanyID",
        related_name='sales_gst_reports'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, db_column="Sales_GST_Report_CreatedAt"
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_column="Sales_GST_Report_UpdatedAt"
    )

    class Meta:
        managed = True
        db_table = "SalesGSTReport"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['client']),
            models.Index(fields=['company']),
        ]

    def __str__(self):
        return f"Sales GST Report {self.key}- {self.date}"
