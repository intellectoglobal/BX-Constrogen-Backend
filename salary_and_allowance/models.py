from django.db import models


class SalaryAndAllowance(models.Model):
    key = models.AutoField(primary_key=True, db_column='Salary&Allowance_Key')
    date = models.DateField(db_column='Salary&Allowance_Date')
    employee = models.ForeignKey(
        'users.AppUser', on_delete=models.CASCADE, db_column='Salary&Allowance_EmpKey')
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='Salary&Allowance__Amount')
    type_choices = [('S', 'Salary'), ('A', 'Allowance')]
    type = models.CharField(
        max_length=1, choices=type_choices, db_column='Salary&Allowance_Type')
    project_key = models.ForeignKey('project.Project', on_delete=models.CASCADE,
                                    db_column='Salary&Allowance__ProjKey', blank=True, null=True)
    payment_mode_key = models.ForeignKey('pricing.Modeofpay', on_delete=models.CASCADE,
                                         db_column='Salary&Allowance__ModeofPayKey', blank=True, null=True)
    account_key = models.ForeignKey('client.BankAccount', on_delete=models.CASCADE,
                                    db_column='Salary&Allowance__AccountKey', blank=True, null=True)
    transaction_detail = models.CharField(
        max_length=255, db_column='Salary&Allowance_TransactionDetail', blank=True, null=True)
    notes = models.CharField(
        max_length=255, db_column='Salary&Allowance_Notes', blank=True, null=True)
    client_id = models.ForeignKey('client.Clientbase', on_delete=models.CASCADE,
                                  db_column='Salary&Allowance_ClientID', blank=True, null=True)
    company_id = models.ForeignKey('client.Company', on_delete=models.CASCADE,
                                   db_column='Salary&Allowance_CompanyID', blank=True, null=True)
    created_by = models.CharField(
        db_column='Salary&Allowance_CreatedBy', max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(
        db_column='Salary&Allowance_CreatedAt', blank=True, null=True, auto_now_add=True)
    updated_by = models.CharField(
        db_column='Salary&Allowance_UpdatedBy', max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(
        db_column='Salary&Allowance_UpdatedAt', blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = 'SalaryAndAllowance'
