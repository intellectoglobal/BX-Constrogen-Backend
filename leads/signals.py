from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Lead, FollowUp, Visit, Comments


@receiver(pre_delete, sender=Lead)
def delete_lead_comments(sender, instance, **kwargs):
    Comments.objects.filter(related_key=instance.pk,
                            comment_type='Lead').delete()


@receiver(pre_delete, sender=Visit)
def delete_visit_comments(sender, instance, **kwargs):
    Comments.objects.filter(related_key=instance.pk,
                            comment_type='Visit').delete()


@receiver(pre_delete, sender=FollowUp)
def delete_followup_comments(sender, instance, **kwargs):
    Comments.objects.filter(related_key=instance.pk,
                            comment_type='FollowUp').delete()
