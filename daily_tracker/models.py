from django.db import models
from project.models import Project, Projectblock, Projectfloor, Projectunit, ProjectSchedule
from estimate.models import WorkCategory
from client.models import Clientbase, Company


class DailyWorkProgressHdr(models.Model):
    key = models.AutoField(
        db_column='DailyWrkProgressHdr_Key', primary_key=True)
    workctgry_key = models.ForeignKey(
        WorkCategory, on_delete=models.CASCADE, db_column='DailyWrkProgressHdr_WrkCtgry_Key')
    project_key = models.ForeignKey(Project, on_delete=models.CASCADE,
                                    db_column='DailyWrkProgressHdr_Proj_Key')
    blk_key = models.ForeignKey(Projectblock, on_delete=models.CASCADE,
                                db_column='DailyWrkProgressHdr_Blk_Key')
    floor_key = models.ForeignKey(Projectfloor, on_delete=models.CASCADE,
                                  db_column='DailyWrkProgressHdr_Flr_Key')
    unit_key = models.ForeignKey(Projectunit, on_delete=models.CASCADE,
                                 db_column='DailyWrkProgressHdr_Unit_Key')
    schedule_key = models.ForeignKey(ProjectSchedule, on_delete=models.CASCADE,
                                 db_column='DailyWrkProgressHdr_Schdle_Key', blank=True, null=True)
    
    STATUS_CHOICES = [
        ('Y', 'Yet to start'),
        ('P', 'In progress'),
        ('C', 'Completed'),
    ]
    status = models.CharField(
        db_column='DailyWrkProgressHdr_Status', max_length=1, choices=STATUS_CHOICES)
    date = models.DateField(
        db_column='DailyWrkProgressHdr_Date', db_index=True)
    created_at = models.DateTimeField(
        db_column='DailyWrkProgressHdr_CreatedAt', auto_now_add=True)
    created_by = models.CharField(
        db_column='DailyWrkProgressHdr_CreatedBy', max_length=255)
    updated_at = models.DateTimeField(
        db_column='DailyWrkProgressHdr_UpdatedAt', auto_now=True, blank=True, null=True)
    updated_by = models.CharField(
        db_column='DailyWrkProgressHdr_UpdatedBy', max_length=255, blank=True, null=True)
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='DailyWrkProgressHdr_Company_ID')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='DailyWrkProgressHdr_Client_ID')

    class Meta:
        managed = True
        db_table = 'DailyWorkProgressHdr'


class DailyWorkProgressDtl(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='DailyWrkProgressDtl_Key')
    descr = models.CharField(
        db_column='DailyWrkProgressDtl_Descr', max_length=255)
    comments = models.CharField(
        db_column='DailyWrkProgressDtl_Cmnts', max_length=255, blank=True, null=True)

    STATUS_CHOICES = [
        ('Y', 'Yet to start'),
        ('P', 'In progress'),
        ('C', 'Completed'),
    ]
    status = models.CharField(
        db_column='DailyWrkProgressDtl_Status', max_length=1, choices=STATUS_CHOICES)
    hdr_key = models.ForeignKey(
        DailyWorkProgressHdr, on_delete=models.CASCADE, db_column='DailyWrkProgressDtl_Hdr_Key', related_name='details')
    created_at = models.DateTimeField(
        db_column='DailyWrkProgressDtl_CreatedAt', auto_now_add=True)
    created_by = models.CharField(
        db_column='DailyWrkProgressDtl_CreatedBy', max_length=255)
    updated_at = models.DateTimeField(
        db_column='DailyWrkProgressDtl_UpdatedAt', auto_now=True, blank=True, null=True)
    updated_by = models.CharField(
        db_column='DailyWrkProgressDtl_UpdatedBy', max_length=255, blank=True, null=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='DailyWrkProgressDtl_Client_ID')

    class Meta:
        managed = True
        db_table = 'DailyWorkProgressDtl'


class DailyWorkProgressImage(models.Model):
    key = models.AutoField(
        primary_key=True, db_column='DailyWrkProgressImage_Key')
    dtl_key = models.ForeignKey(DailyWorkProgressDtl, on_delete=models.CASCADE,
                                db_column='DailyWrkProgressImage_Dtl_Key', related_name='images')
    image_url = models.TextField(db_column='DailyWrkProgressImage_URL')
    caption = models.CharField(max_length=255, db_column='DailyWrkProgressImage_Caption',
                               blank=True, null=True)
    created_at = models.DateTimeField(db_column='DailyWrkProgressImage_CreatedAt', blank=True, null=True)
    created_by = models.CharField(
        max_length=255, db_column='DailyWrkProgressImage_CreatedBy')
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column='DailyWrkProgressImage_Client_ID')

    class Meta:
        managed = True
        db_table = 'DailyWorkProgressImage'
