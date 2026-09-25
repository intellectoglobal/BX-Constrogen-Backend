from django.db import models
from client.models import Company, Clientbase
from django.core.validators import RegexValidator


class LeadStatus(models.Model):
    key = models.AutoField(db_column="LeadStatus_Key", primary_key=True)
    name = models.CharField(db_column="LeadStatus_Name", max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="LeadStatus_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="LeadStatus_Company_ID")

    class Meta:
        managed = True
        db_table = "LeadStatus"


class LeadSourceCategory(models.Model):
    key = models.AutoField(db_column='LeadSourceCtgry_Key', primary_key=True)
    descr = models.CharField(db_column='LeadSourceCtgry_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="LeadSourceCtgry_Client_ID")

    class Meta:
        managed = True
        db_table = 'LeadSourceCategory'


class LeadSource(models.Model):
    key = models.AutoField(db_column='LeadSource_Key', primary_key=True)
    descr = models.CharField(db_column='LeadSource_Descr', max_length=100)
    category_id = models.ForeignKey(
        LeadSourceCategory,on_delete=models.CASCADE, db_column="LeadSource_Ctgry_ID"
    )
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="LeadSource_Client_ID")

    class Meta:
        managed = True
        db_table = 'LeadSource'

class BudgetRanges(models.Model):
    key = models.AutoField(db_column='BudgetRanges_Key', primary_key=True)
    descr = models.CharField(db_column='BudgetRanges_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="BudgetRanges_Client_ID")

    class Meta:
        managed = True
        db_table = 'BudgetRanges'

class ProjectInterests(models.Model):
    key = models.AutoField(db_column='ProjectInt_Key', primary_key=True)
    descr = models.CharField(db_column='ProjectInt_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="ProjectInt_Client_ID")

    class Meta:
        managed = True
        db_table = 'ProjectInterests'


class FloorPreference(models.Model):
    key = models.AutoField(db_column='FloorsPref_Key', primary_key=True)
    descr = models.CharField(db_column='FloorsPref_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FloorsPref_Client_ID")

    class Meta:
        managed = True
        db_table = 'FloorsPreference'


class FacingPreference(models.Model):
    key = models.AutoField(db_column='FacingPref_Key', primary_key=True)
    descr = models.CharField(db_column='FacingPref_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FacingPref_Client_ID")

    class Meta:
        managed = True
        db_table = 'FacingPreference'


class FollowUpStages(models.Model):
    key = models.AutoField(db_column='FollowUpStages_Key', primary_key=True)
    descr = models.CharField(db_column='FollowUpStages_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FollowUpStages_Client_ID")

    class Meta:
        managed = True
        db_table = 'FollowUpStages'


class Occupancies(models.Model):
    key = models.AutoField(db_column='Occupancies_Key', primary_key=True)
    descr = models.CharField(db_column='Occupancies_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="Occupancies_Client_ID")

    class Meta:
        managed = True
        db_table = 'Occupancies'

class OccupancySubTypes(models.Model):
    key = models.AutoField(db_column='OccupancySubTyp_Key', primary_key=True)
    descr = models.CharField(db_column='OccupancySubTyp_Descr', max_length=100)
    occup_id = models.ForeignKey(
        Occupancies, on_delete=models.CASCADE, db_column="OccupancySubTyp_Occup_ID", null=True, blank=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="OccupancySubTyp_Client_ID")

    class Meta:
        managed = True
        db_table = 'OccupancySubTypes'

class LocationPreference(models.Model):
    key = models.AutoField(db_column='LocationPref_Key', primary_key=True)
    descr = models.CharField(db_column='LocationPref_Descr', max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="LocationPref_Client_ID")

    class Meta:
        managed = True
        db_table = 'LocationPreference'

class Lead(models.Model):
    key = models.AutoField(db_column="Lead_Key", primary_key=True)
    lead_no = models.CharField(db_column="Lead_No", max_length=10, unique=True)
    lead_name = models.CharField(db_column="Lead_Name",
                                 max_length=255, blank=True, null=True)
    enquiry_date = models.DateField(
        db_column="Lead_EnquiryDate", blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Invalid Phonenumber")
    contact_1 = models.CharField(
        validators=[phone_regex], db_column="Lead_Contact1", max_length=20, unique=True)
    contact_2 = models.CharField(
        validators=[phone_regex], db_column="Lead_Contact2", max_length=20, null=True, blank=True)
    budget = models.IntegerField(db_column="Lead_Budget", null=True, blank=True)
    email = models.CharField(db_column="Lead_Email",
                             max_length=100, null=True, blank=True)
    status_key = models.ForeignKey(
        LeadStatus, on_delete=models.CASCADE, db_column="Lead_StatusKey")
    budget_rng_key = models.ForeignKey(
        BudgetRanges, on_delete=models.CASCADE, db_column="Lead_BudgetRng_Key", blank=True, null=True)
    lead_src_ctgry_key = models.ForeignKey(
        LeadSourceCategory, on_delete=models.CASCADE, db_column="Lead_LeadSrcCtgry_Key", blank=True, null=True)
    lead_src_key = models.ForeignKey(
        LeadSource, on_delete=models.CASCADE, db_column="Lead_LeadSrc_Key", blank=True, null=True)
    property_interest_key = models.ForeignKey(
        ProjectInterests, on_delete=models.CASCADE, db_column="Lead_PrprtyInt_Key", blank=True, null=True)
    floor_pref_key = models.ForeignKey(
        FloorPreference, on_delete=models.CASCADE, db_column="Lead_FloorPref_Key", blank=True, null=True)
    occupancies_key = models.ForeignKey(
        Occupancies, on_delete=models.CASCADE, db_column="Lead_Occupancies_Key", blank=True, null=True)
    occupa_subtyp_key = models.ForeignKey(
        OccupancySubTypes, on_delete=models.CASCADE, db_column="Lead_OccupaSubTyp_Key", blank=True, null=True)
    follow_upstg_key = models.ForeignKey(
        FollowUpStages, on_delete=models.CASCADE, db_column="Lead_FollowUpStg_Key", blank=True, null=True)
    createdby = models.CharField(
        db_column='Lead_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Lead_CreatedDtTm', blank=True, null=True, auto_now_add=True)
    lastmodifiedby = models.CharField(
        db_column='Lead_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Lead_LastModifiedDtTm', blank=True, null=True, auto_now=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="Lead_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="Lead_Company_ID")

    class Meta:
        managed = True
        db_table = "Lead"

class LeadFacingPreference(models.Model):
    key = models.AutoField(db_column='LeadFacingPref_Key', primary_key=True)
    lead_key = models.ForeignKey(
        Lead, on_delete=models.CASCADE, db_column='LeadFacingPref_Lead_Key', blank=True, null=True)
    facingpref_key = models.ForeignKey(
        FacingPreference, on_delete=models.CASCADE, db_column='LeadFacingPref_FacingPref_Key', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='LeadFacingPref_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='LeadFacingPref_Client_ID')
    
    class Meta:
        managed = True
        db_table = 'LeadFacingPreference'

class LeadLocationPreference(models.Model):
    key = models.AutoField(db_column='LeadLocPref_Key', primary_key=True)
    lead_key = models.ForeignKey(
        Lead, on_delete=models.CASCADE, db_column='LeadLocPref_Lead_Key', blank=True, null=True)
    locationpref_key = models.ForeignKey(
        LocationPreference, on_delete=models.CASCADE, db_column='LeadLocPref_LeadPref_Key', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='LeadLocPref_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='LeadLocPref_Client_ID')
    
    class Meta:
        managed = True
        db_table = 'LeadLocationPreferance'

class LeadProjectPreference(models.Model):
    key = models.AutoField(db_column='LeadProjectPref_Key', primary_key=True)
    lead_key = models.ForeignKey(
        Lead, on_delete=models.CASCADE, db_column='LeadProjectPref_Lead_Key', blank=True, null=True)
    project_key = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, db_column='LeadProjectPref_Proj_Key', blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column='LeadProjectPref_Company_ID')
    client_id = models.ForeignKey(Clientbase, on_delete=models.CASCADE,
                                  db_column='LeadProjectPref_Client_ID')
    class Meta:
        managed = True
        db_table = 'LeadProjectPreference'

class VisitStatus(models.Model):
    key = models.AutoField(db_column="VisitStatus_Key", primary_key=True)
    name = models.CharField(db_column="VisitStatus_Name", max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="VisitStatus_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="VisitStatus_Company_ID")

    class Meta:
        managed = True
        db_table = "VisitStatus"


class Visit(models.Model):
    key = models.AutoField(db_column="Visit_Key", primary_key=True)
    lead_key = models.ForeignKey(
        Lead, on_delete=models.CASCADE, db_column="Visit_LeadKey")
    visit_date = models.DateField(db_column="Visit_Date")
    visit_time = models.CharField(db_column="Visit_Time", max_length=20)
    project_key = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, db_column="Visit_ProjKey", blank=True, null=True)
    agent_name = models.CharField(db_column="Visit_AgentName", max_length=255, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Invalid Phonenumber")
    agent_phone = models.CharField(
        validators=[phone_regex], db_column="Visit_AgentPhone", max_length=20, blank=True, null=True)
    status_key = models.ForeignKey(
        VisitStatus, on_delete=models.CASCADE, db_column="Visit_StatusKey")
    createdby = models.CharField(
        db_column='Visit_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Visit_CreatedDtTm', blank=True, null=True, auto_now_add=True)
    lastmodifiedby = models.CharField(
        db_column='Visit_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Visit_LastModifiedDtTm', blank=True, null=True, auto_now=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="Visit_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="Visit_Company_ID")

    class Meta:
        managed = True
        db_table = "Visit"


class FollowUpStatus(models.Model):
    key = models.AutoField(db_column="FollowUpStatus_Key", primary_key=True)
    name = models.CharField(db_column="FollowUpStatus_Name", max_length=100)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FollowUpStatus_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="FollowUpStatus_Company_ID")

    class Meta:
        managed = True
        db_table = "FollowUpStatus"

class FeedBack(models.Model):
    key = models.AutoField(db_column='Feedback_Key', primary_key=True)
    descr = models.CharField(db_column='Feedback_Descr', max_length=255)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="Feedback_Client_ID")

    class Meta:
        managed = True
        db_table = 'Feedback'

class FeedBackDetails(models.Model):
    key = models.AutoField(db_column='FeedBackDetails_Key', primary_key=True)
    descr = models.CharField(db_column='FeedBackDetails_Descr', max_length=255)
    feedback_id = models.ForeignKey(
        FeedBack, on_delete=models.CASCADE, db_column="FeedBackDetails_Feedback_ID", null=True, blank=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FeedBackDetails_Client_ID")

    class Meta:
        managed = True
        db_table = 'FeedBackDetails'

class FollowUp(models.Model):
    key = models.AutoField(db_column="FollowUp_Key", primary_key=True)
    lead_key = models.ForeignKey(
        Lead, on_delete=models.CASCADE, db_column="FollowUp_LeadKey")
    days_since_enquiry = models.IntegerField(
        db_column="FollowUp_DaysSinceEnq", blank=True, null=True)
    last_followup_date = models.DateField(db_column="FollowUp_Date")
    followup_time = models.CharField(db_column="FollowUp_Time", max_length=20)
    status_key = models.ForeignKey(
        FollowUpStatus, on_delete=models.CASCADE, db_column="FollowUp_StatusKey", blank=True, null=True)
    follow_notes = models.CharField(
        db_column="FollowUp_Notes", max_length=500, blank=True, null=True)
    employee_key = models.ForeignKey(
        "users.AppUser", on_delete=models.CASCADE, db_column="FollowUp_EmpKey", blank=True, null=True)
    feedback_key = models.ForeignKey(
        FeedBack, on_delete=models.CASCADE, db_column="FollowUp_Feedback_ID", blank=True, null=True)
    followup_details_key = models.ForeignKey(
        FeedBackDetails, on_delete=models.CASCADE, db_column="FollowUp_FeedbackDetails_ID", blank=True, null=True)
    createdby = models.CharField(
        db_column='FollowUp_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='FollowUp_CreatedDtTm', blank=True, null=True, auto_now_add=True)
    lastmodifiedby = models.CharField(
        db_column='FollowUp_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='FollowUp_LastModifiedDtTm', blank=True, null=True, auto_now=True)
    client_id = models.ForeignKey(
        Clientbase, on_delete=models.CASCADE, db_column="FollowUp_Client_ID")
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_column="FollowUp_Company_ID")

    class Meta:
        managed = True
        db_table = "FollowUp"


class Comments(models.Model):
    key = models.AutoField(db_column="Comments_Key", primary_key=True)
    related_key = models.IntegerField(
        db_column="Comments_RelatedKey", blank=True, null=True)
    COMMENTS_CHOICES = (
        ("Lead", "Lead"),
        ("FollowUp", "FollowUp"),
        ("Visit", "Visit")
    )
    comment_type = models.CharField(
        db_column="Comments_Type", max_length=20, blank=True, null=True, choices=COMMENTS_CHOICES)
    comment = models.TextField(db_column="Comments_Comment")
    createdby = models.CharField(
        db_column='Comments_CreatedBy', max_length=100, blank=True, null=True)
    createddttm = models.DateTimeField(
        db_column='Comments_CreatedDtTm', blank=True, null=True, auto_now_add=True)
    lastmodifiedby = models.CharField(
        db_column='Comments_LastModifiedBy', max_length=100, blank=True, null=True)
    lastmodifieddttm = models.DateTimeField(
        db_column='Comments_LastModifiedDtTm', blank=True, null=True, auto_now=True)

    class Meta:
        managed = True
        db_table = "CRMComments"
