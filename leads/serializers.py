from .models import LeadStatus, Lead, VisitStatus, Visit, FollowUpStatus, FollowUp, Comments, LeadSourceCategory,LeadSource,BudgetRanges,ProjectInterests,FloorPreference,FacingPreference,FollowUpStages,Occupancies,OccupancySubTypes,LocationPreference,LeadLocationPreference,LeadProjectPreference,LeadFacingPreference,FeedBack,FeedBackDetails
from project.models import Projectunit, ProjectElevationDiagrams, Project, Projstatushistory
from project.serializers import ProjStatusHistorySerializer, ProjectStatusSerializer
from rest_framework import serializers
from buildiq.super_serializer import DynamicFieldsModelSerializer
from datetime import datetime


class LeadStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = LeadStatus
        fields = '__all__'

class LeadProjectSerializer(DynamicFieldsModelSerializer):
    createddttm = serializers.DateTimeField(
        default=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    # state = StateSerializer(source='state_key', read_only=True)
    # city = CitySerializer(source='city_key',
    #                       read_only=True, fields=('key', 'name'))
    status = ProjectStatusSerializer(source='projstatus_key',
                                      read_only=True, fields=('key', 'descr'))
    # pro_type = ProjectTypeSerializer(source='projtyp_key',
    #                                  read_only=True, fields=('key', 'id', 'descr'))
    # no_of_units = serializers.SerializerMethodField(read_only=True)

    latest_proj_status = serializers.SerializerMethodField(read_only=True)
    latest_proj_price = serializers.SerializerMethodField(read_only=True)

    def get_latest_proj_status(self, project):
        if Projstatushistory.objects.filter(proj_key=project).exists():
            proStsHis = Projstatushistory.objects.filter(
                proj_key=project).latest("createddttm")
            return ProjStatusHistorySerializer(proStsHis).data['proj_status']
        return {}

    # def get_latest_proj_price(self, project):
    #     if Projpricehistory.objects.filter(proj_key=project).exists():
    #         proStsHis = Projpricehistory.objects.filter(
    #             proj_key=project).latest("createddttm")
    #         return {"effprice": ProjPriceHistorySerializer(proStsHis).data["effprice"]}
    #     return {}

    # def get_no_of_units(self, project):
    #     return Projectunit.objects.filter(proj_key=project).count()

    class Meta:
        model = Project
        fields = '__all__'

class LeadSourceCategorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = LeadSourceCategory
        fields = '__all__'

class LeadSourceSerializer(DynamicFieldsModelSerializer):
    lead_src_ctgry_key = serializers.SerializerMethodField()

    def get_lead_src_ctgry_key(self, obj):
        return obj.category_id.key

    class Meta:
        model = LeadSource
        fields = '__all__'

class BudgetRangesSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BudgetRanges
        fields = '__all__'

class ProjectInterestsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProjectInterests
        fields = '__all__'

class FloorPrefSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FloorPreference
        fields = '__all__'

class FacingPrefSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FacingPreference
        fields = '__all__'

class FollowUpStagesSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FollowUpStages
        fields = '__all__'

class OccupanciesSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Occupancies
        fields = '__all__'

class OccupancySubTypesSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = OccupancySubTypes
        fields = '__all__'

class LocationPreferenceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = LocationPreference
        fields = '__all__'


class LeadLocationPreferenceSerializer(DynamicFieldsModelSerializer):
    location_descr = serializers.CharField(
        source='locationpref_key.descr', read_only=True)

    class Meta:
        model = LeadLocationPreference
        fields = '__all__'

class LeadFacingPreferenceSerializer(DynamicFieldsModelSerializer):
    facing_descr = serializers.CharField(
        source='facingpref_key.descr', read_only=True)

    class Meta:
        model = LeadFacingPreference
        fields = '__all__'

class LeadProjectPreferenceSerializer(DynamicFieldsModelSerializer):
    project_name = serializers.SerializerMethodField()

    def get_project_name(self, obj):
        return getattr(obj.project_key, 'name', None) if obj.project_key else None

    class Meta:
        model = LeadProjectPreference
        fields = '__all__'


class LeadSerializer(DynamicFieldsModelSerializer):
    enquiry_date = serializers.DateField(
        format='%d-%b-%Y',
        input_formats=['%d-%b-%Y'],
        required=False
    )
    status_name = serializers.CharField(
        source="status_key.name", read_only=True)
    property_name = serializers.SerializerMethodField()
    project_pref_keys = serializers.SerializerMethodField()
    facing_pref_keys = serializers.SerializerMethodField()
    lead_src = serializers.SerializerMethodField()
    lead_src_ctgry = serializers.SerializerMethodField()

    def get_property_name(self, obj):
        visit = Visit.objects.filter(lead_key=obj).select_related('project_key').first()
        if visit and visit.project_key:
            return visit.project_key.name
        return None

    def get_project_pref_keys(self, obj):
        return [
            {'key': pref.project_key.key, 'descr': pref.project_key.name}
            for pref in obj.leadprojectpreference_set.select_related('project_key').all()
            if pref.project_key
        ]

    def get_facing_pref_keys(self, obj):
        return [
            {'key': pref.facingpref_key.key, 'descr': pref.facingpref_key.descr}
            for pref in obj.leadfacingpreference_set.select_related('facingpref_key').all()
            if pref.facingpref_key
        ]

    def get_lead_src(self, obj):
        return {'key': obj.lead_src_key.key, 'descr': obj.lead_src_key.descr} if obj.lead_src_key else None

    def get_lead_src_ctgry(self, obj):
        return {'key': obj.lead_src_ctgry_key.key, 'descr': obj.lead_src_ctgry_key.descr} if obj.lead_src_ctgry_key else None

    def validate_contact_1(self, value):
        qs = Lead.objects.filter(contact_1=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        existing = qs.first()
        if existing:
            lead_name = existing.lead_name or "Lead"
            raise serializers.ValidationError(
                f'Number already associated with "{lead_name}"'
            )
        return value

    class Meta:
        model = Lead
        fields = '__all__'


class VisitStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = VisitStatus
        fields = '__all__'


class VisitSerializer(DynamicFieldsModelSerializer):
    visit_date = serializers.DateField(
         format='%d-%b-%Y',
        input_formats=['%d-%b-%Y'],
    )
    status = VisitStatusSerializer(source='status_key', read_only=True)
    project_name = serializers.SerializerMethodField()
    leadno = serializers.CharField(
        source='lead_key.lead_no', read_only=True)
    lead_name = serializers.CharField(
        source='lead_key.lead_name', read_only=True)
    contact_1 = serializers.CharField(
        source='lead_key.contact_1', read_only=True)
    lead_status = serializers.CharField(
        source='lead_key.status_key.name', read_only=True)
    project_preferences = serializers.SerializerMethodField()
    project_pref_keys = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    source_category = serializers.SerializerMethodField()
    lead_src_key = serializers.SerializerMethodField()
    lead_src_ctgry_key = serializers.SerializerMethodField()

    def get_project_name(self, obj):
        return getattr(obj.project_key, 'name', None) if obj.project_key else None

    def get_project_preferences(self, obj):
        prefs = obj.lead_key.leadprojectpreference_set.select_related(
            "project_key"
        ).values_list("project_key__name", flat=True)
        return ", ".join(prefs)

    def get_project_pref_keys(self, obj):
        return [
            pref.project_key.key
            for pref in obj.lead_key.leadprojectpreference_set.select_related('project_key').all()
            if pref.project_key
        ]

    def get_source(self, obj):
        return getattr(obj.lead_key.lead_src_key, 'descr', '') if obj.lead_key.lead_src_key else ''

    def get_source_category(self, obj):
        return getattr(obj.lead_key.lead_src_ctgry_key, 'descr', '') if obj.lead_key.lead_src_ctgry_key else ''

    def get_lead_src_key(self, obj):
        return obj.lead_key.lead_src_key.key if obj.lead_key.lead_src_key else None

    def get_lead_src_ctgry_key(self, obj):
        return obj.lead_key.lead_src_ctgry_key.key if obj.lead_key.lead_src_ctgry_key else None

    class Meta:
        model = Visit
        fields = '__all__'


class FollowUpStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FollowUpStatus
        fields = '__all__'


class FollowUpSerializer(DynamicFieldsModelSerializer):
    last_followup_date = serializers.DateField(
        format='%d-%b-%Y',
        input_formats=['%d-%b-%Y'],
    )
    status = FollowUpStatusSerializer(source='status_key', read_only=True)
    leadno = serializers.CharField(
        source='lead_key.lead_no', read_only=True)
    lead_name = serializers.CharField(
        source='lead_key.lead_name', read_only=True)
    contact_1 = serializers.CharField(
        source='lead_key.contact_1', read_only=True)
    lead_status = serializers.CharField(
        source='lead_key.status_key.name', read_only=True)
    feedback = serializers.SerializerMethodField()
    followup_details = serializers.SerializerMethodField()

    def get_feedback(self, obj):
        return {'key': obj.feedback_key.key, 'descr': obj.feedback_key.descr} if obj.feedback_key else None

    def get_followup_details(self, obj):
        return {'key': obj.followup_details_key.key, 'descr': obj.followup_details_key.descr} if obj.followup_details_key else None

    class Meta:
        model = FollowUp
        fields = '__all__'

class FeedbackSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FeedBack
        fields = '__all__'

class FeedbackDetailsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FeedBackDetails
        fields = '__all__'


class LeadDetailSerializer(DynamicFieldsModelSerializer):
    enquiry_date = serializers.DateField(
        format='%d-%b-%Y',
        input_formats=['%d-%b-%Y'],
        required=False
    )
    status_name = serializers.SerializerMethodField(read_only=True)
    visit = VisitSerializer(many=True, source='visit_set', read_only=True)
    followup = FollowUpSerializer(
        many=True, source='followup_set', read_only=True)
    location_pref_keys = serializers.SerializerMethodField()
    facing_pref_keys = serializers.SerializerMethodField()
    project_pref_keys = serializers.SerializerMethodField()
    lead_src = serializers.SerializerMethodField()
    lead_src_ctgry = serializers.SerializerMethodField()

    def get_status_name(self, obj):
        if obj.status_key:
            return obj.status_key.name
        return None
    def get_location_pref_keys(self, obj):
        return [
            {'key': pref.locationpref_key.key, 'descr': pref.locationpref_key.descr}
            for pref in obj.leadlocationpreference_set.all()
        ]

    def get_facing_pref_keys(self, obj):
        return [
            {'key': pref.facingpref_key.key, 'descr': pref.facingpref_key.descr}
            for pref in obj.leadfacingpreference_set.select_related('facingpref_key').all()
            if pref.facingpref_key
        ]

    def get_project_pref_keys(self, obj):
        return [
            {'key': pref.project_key.key, 'descr': pref.project_key.name}
            for pref in obj.leadprojectpreference_set.select_related('project_key').all()
            if pref.project_key
        ]

    def get_lead_src(self, obj):
        return {'key': obj.lead_src_key.key, 'descr': obj.lead_src_key.descr} if obj.lead_src_key else None

    def get_lead_src_ctgry(self, obj):
        return {'key': obj.lead_src_ctgry_key.key, 'descr': obj.lead_src_ctgry_key.descr} if obj.lead_src_ctgry_key else None

    class Meta:
        model = Lead
        fields = '__all__'
        extra_fields = ('visit', 'followup', 'status_name', 'location_pref_keys', 'facing_pref_keys', 'project_pref_keys', 'lead_src_key', 'lead_src_ctgry_key')


class CommentsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class PropertiesSerializer(DynamicFieldsModelSerializer):
    image_url = serializers.SerializerMethodField()
    project = serializers.CharField(
        source='proj_key.name', read_only=True)
    address = serializers.CharField(
        source='proj_key.addr1', read_only=True)
    status = serializers.CharField(
        source='projunit_status_key.descr', read_only=True, default='Available')

    def get_image_url(self, obj):
        elevation = ProjectElevationDiagrams.objects.filter(
            project_id=obj.proj_key, block_id=obj.projblk_key)
        if elevation.exists():
            return elevation.first().image_url
        return None

    class Meta:
        model = Projectunit
        fields = ['image_url', 'project', 'descr', 'address', 'base_price',
                  'bedrooms', 'carpetarea', 'saleablearea', 'udsarea', 'facing', 'status', 'id']


class ExportReportSerializer(DynamicFieldsModelSerializer):
    status = serializers.CharField(source='status_key.name', read_only=True)

    budget_range = serializers.SerializerMethodField()
    property_interest = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    source_category = serializers.SerializerMethodField()
    floor_preference = serializers.SerializerMethodField()
    facing_preference = serializers.SerializerMethodField()
    occupancy = serializers.SerializerMethodField()
    occupancy_sub_type = serializers.SerializerMethodField()
    follow_up_stage = serializers.SerializerMethodField()
    location_preferences = serializers.SerializerMethodField()
    project_preferences = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    follow_up = serializers.SerializerMethodField()
    site_visit = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    junk_leads = serializers.SerializerMethodField()
    active_followup = serializers.SerializerMethodField()
    JUNK_FEEDBACK_VALUES = {
        'irrelevantcall',
        'irrelevantcalls',
        'unansweredcall',
        'unansweredcalls',
    }
    ACTIVE_FOLLOWUP_STATUS_VALUES = {'open', 'potential'}
   
    def get_budget_range(self, obj):
        return getattr(obj.budget_rng_key, "descr", "")

    def get_property_interest(self, obj):
        return getattr(obj.property_interest_key, "descr", "")

    def get_source(self, obj):
        return getattr(obj.lead_src_key, "descr", "")

    def get_source_category(self, obj):
        return getattr(obj.lead_src_ctgry_key, "descr", "")

    def get_floor_preference(self, obj):
        return getattr(obj.floor_pref_key, "descr", "")

    def get_facing_preference(self, obj):
        prefs = obj.leadfacingpreference_set.select_related(
            "facingpref_key"
        ).values_list("facingpref_key__descr", flat=True)
        return ", ".join(prefs)

    def get_occupancy(self, obj):
        return getattr(obj.occupancies_key, "descr", "")

    def get_occupancy_sub_type(self, obj):
        return getattr(obj.occupa_subtyp_key, "descr", "")

    def get_follow_up_stage(self, obj):
        return getattr(obj.follow_upstg_key, "descr", "")

    def get_location_preferences(self, obj):
        prefs = obj.leadlocationpreference_set.select_related(
            "locationpref_key"
        ).values_list("locationpref_key__descr", flat=True)
        return ", ".join(prefs)

    def get_project_preferences(self, obj):
        prefs = obj.leadprojectpreference_set.select_related(
            "project_key"
        ).values_list("project_key__name", flat=True)
        return ", ".join(prefs)

    def get_project_name(self, obj):
        visit = Visit.objects.filter(
            lead_key=obj
        ).select_related("project_key").first()
        return getattr(visit.project_key, "name", "") if visit else ""

    def get_comments(self, obj):
        """Lead-level comments"""
        comments = Comments.objects.filter(
            comment_type="Lead",
            related_key=obj.key
        )
        serializer = CommentsSerializer(
            comments, many=True, fields=['comment', 'createdby', 'createddttm'])
        return serializer.data

    def get_follow_up(self, obj):
        """Follow-up data with embedded comments"""
        follow_ups = FollowUp.objects.filter(lead_key=obj.key)
        data = []
        for follow_up in follow_ups:
            feedback_descr = getattr(follow_up.feedback_key, 'descr', '')
            normalized_feedback = ''.join(ch for ch in feedback_descr.lower() if ch.isalnum())
            # Followup sheet should not include Irrelevant call entries.
            if normalized_feedback in {'irrelevantcall', 'irrelevantcalls'}:
                continue

            comments = Comments.objects.filter(
                comment_type="FollowUp", related_key=follow_up.key
            )
            comments_serialized = CommentsSerializer(
                comments, many=True, fields=['comment', 'createdby', 'createddttm']).data
            followup_data = FollowUpSerializer(
                follow_up,
                fields=['last_followup_date', 'followup_time','feedback', 'followup_details',
                        'follow_notes', 'status', 'createdby']
            ).data
            followup_data['lead_name'] = obj.lead_name  # Add lead name
            followup_data['comments'] = comments_serialized
            data.append(followup_data)
        return data

    def get_site_visit(self, obj):
        """Site visit data with embedded comments"""
        site_visits = Visit.objects.filter(lead_key=obj.key)
        data = []
        for visit in site_visits:
            comments = Comments.objects.filter(
                comment_type="Visit", related_key=visit.key
            )
            comments_serialized = CommentsSerializer(
                comments, many=True, fields=['comment', 'createdby', 'createddttm']).data
            visit_data = VisitSerializer(
                visit,
                fields=['visit_date', 'visit_time', 'property_preference',
                        'source','source_category','status', 'createdby']
            ).data
            visit_data['lead_name'] = obj.lead_name  # Add lead name
            visit_data['comments'] = comments_serialized
            data.append(visit_data)
        return data

    def get_junk_leads(self, obj):
        """Junk leads sheet rows: only Irrelevant call / Unanswered calls feedback."""
        follow_ups = FollowUp.objects.filter(lead_key=obj.key)
        data = []

        for follow_up in follow_ups:
            feedback_descr = getattr(follow_up.feedback_key, 'descr', '')
            normalized_feedback = ''.join(ch for ch in feedback_descr.lower() if ch.isalnum())
            if normalized_feedback not in self.JUNK_FEEDBACK_VALUES:
                continue

            followup_details_descr = ''
            if follow_up.followup_details_key:
                followup_details_descr = follow_up.followup_details_key.descr

            data.append({
                'lead_no': obj.lead_no,
                'lead_name': obj.lead_name,
                'followup_date': follow_up.last_followup_date,
                'followup_time': follow_up.followup_time,
                'feedback': feedback_descr,
                'feedback_details': followup_details_descr,
                'remarks': follow_up.follow_notes,
            })
        return data

    def get_active_followup(self, obj):
        """Active Follow-Up sheet rows: same lead-sheet data for Open/Potential leads only."""
        status_name = getattr(obj.status_key, 'name', '')
        normalized_status = ''.join(ch for ch in status_name.lower() if ch.isalnum())
        if normalized_status not in self.ACTIVE_FOLLOWUP_STATUS_VALUES:
            return []

        return [{
            'lead_no': obj.lead_no,
            'lead_name': obj.lead_name,
            'enquiry_date': obj.enquiry_date,
            'contact_1': obj.contact_1,
            'contact_2': obj.contact_2,
            'budget': obj.budget,
            'budget_range': self.get_budget_range(obj),
            'email': obj.email,
            'property_interest': self.get_property_interest(obj),
            'source': self.get_source(obj),
            'source_category': self.get_source_category(obj),
            'floor_preference': self.get_floor_preference(obj),
            'facing_preference': self.get_facing_preference(obj),
            'occupancy': self.get_occupancy(obj),
            'occupancy_sub_type': self.get_occupancy_sub_type(obj),
            'follow_up_stage': self.get_follow_up_stage(obj),
            'location_preferences': self.get_location_preferences(obj),
            'project_preferences': self.get_project_preferences(obj),
            'project_name': self.get_project_name(obj),
            'createdby': obj.createdby,
            'status': status_name,
        }]

    class Meta:
        model = Lead
        fields = [
            'lead_no', 'lead_name', 'enquiry_date','contact_1', 'contact_2', 'budget','budget_range', 'email',
            'property_interest', 'source', 'source_category','floor_preference', 'facing_preference','occupancy',
            'occupancy_sub_type','follow_up_stage', 'location_preferences', 'project_preferences','project_name', 'follow_up', 'site_visit',
            'comments', 'createdby', 'status', 'follow_up', 'site_visit', 'comments',
            'junk_leads', 'active_followup'
        ]

class JunkLeadsSerializer(DynamicFieldsModelSerializer):
    # Lead fields
    lead_key = serializers.IntegerField(source="lead_key.key", read_only=True)
    lead_no = serializers.CharField(source="lead_key.lead_no", read_only=True)
    lead_name = serializers.CharField(source="lead_key.lead_name", read_only=True)
    contact_1 = serializers.CharField(source="lead_key.contact_1", read_only=True)
    budget = serializers.DecimalField(
        source="lead_key.budget",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    status_name = serializers.CharField(
        source="lead_key.status_key.name",
        read_only=True
    )

    property_name = serializers.SerializerMethodField()
    project_pref = serializers.SerializerMethodField()
    lead_src = serializers.SerializerMethodField()
    lead_src_ctgry = serializers.SerializerMethodField()

    # FollowUp fields - Make feedback_key and followup_details_key writable
    last_followup_date = serializers.DateField(read_only=True)
    followup_time = serializers.TimeField(read_only=True)
    feedback_name = serializers.CharField(
        source="feedback_key.name",
        read_only=True
    )
    feedback_key = serializers.PrimaryKeyRelatedField(
        queryset=FeedBack.objects.all(),
        write_only=True,
        required=False
    )
    followup_details_key = serializers.PrimaryKeyRelatedField(
        queryset=FeedBackDetails.objects.all(),
        write_only=True,
        required=False
    )
    feedback = serializers.SerializerMethodField()
    followup_details = serializers.SerializerMethodField()

    def get_feedback(self, obj):
        return {'key': obj.feedback_key.key, 'descr': obj.feedback_key.descr} if obj.feedback_key else None

    def get_followup_details(self, obj):
        return {'key': obj.followup_details_key.key, 'descr': obj.followup_details_key.descr} if obj.followup_details_key else None

    def get_property_name(self, obj):
        visit = Visit.objects.filter(
            lead_key=obj.lead_key
        ).select_related("project_key").first()

        return visit.project_key.name if visit and visit.project_key else None

    def get_project_pref(self, obj):
        return [
            {
                "key": pref.project_key.key,
                "descr": pref.project_key.name
            }
            for pref in obj.lead_key.leadprojectpreference_set
            .select_related("project_key")
            .all()
            if pref.project_key
        ]

    def get_lead_src(self, obj):
        lead = obj.lead_key
        return (
            {"key": lead.lead_src_key.key, "descr": lead.lead_src_key.descr}
            if lead.lead_src_key else None
        )

    def get_lead_src_ctgry(self, obj):
        lead = obj.lead_key
        return (
            {"key": lead.lead_src_ctgry_key.key, "descr": lead.lead_src_ctgry_key.descr}
            if lead.lead_src_ctgry_key else None
        )

    def get_location_pref(self, obj):
        return [
            {
                "key": pref.locationpref_key.key,
                "descr": pref.locationpref_key.descr
            }
            for pref in obj.lead_key.leadlocationpreference_set
            .select_related("locationpref_key")
            .all()
            if pref.locationpref_key
        ]

    class Meta:
        model = FollowUp
        fields = '__all__'
