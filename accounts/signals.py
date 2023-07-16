from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        models.UserProfile.objects.create(user=instance)
    else:
        try:
            profile = models.UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the userprofile if not exist
            models.UserProfile.objects.create(user=instance)
