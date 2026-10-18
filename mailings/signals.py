from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Attempt
from .services import stats_key


@receiver([post_save, post_delete], sender=Attempt)
def drop_stats_cache(sender, instance, **kwargs):
    try:
        cache.delete(stats_key(instance.mailing.owner_id))
    except Exception:
        pass
