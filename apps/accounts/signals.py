from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import NotificationPreference, StudentProfile, StudyPreference, User


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)
        StudyPreference.objects.create(user=instance)
        NotificationPreference.objects.create(user=instance)
