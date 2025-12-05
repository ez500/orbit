from django.db.models.signals import post_save
from django.dispatch import receiver

from company.models import Announcement, CompanyMembership
from dashboard.models import Notification


@receiver(post_save, sender=Announcement)
def create_announcement_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    company = instance.company

    memberships = CompanyMembership.objects.filter(company=company).select_related("user")

    for membership in memberships:
        user = membership.user
        Notification.objects.create(
            user=user,
            message=f"New announcement in {company.name}: {instance.title}",
            announcement=instance
        )
