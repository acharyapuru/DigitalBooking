from celery import shared_task
import logging
from datetime import datetime
from django.utils import timezone
from .models import ShowDay, ShowTime, Booking

logger = logging.getLogger(__name__)

@shared_task
def delete_old_show_days():
    try:
        ShowDay.objects.filter(day__lt=datetime.now()).delete()
        logger.info("Old show days deleted successfully.")
    except Exception as e:
        logger.error(f"Error in delete_old_show_days: {e}")
        raise

@shared_task
def delete_old_show_times():
    try:
        ShowTime.objects.filter(time__lt=datetime.now().time()).delete()
        logger.info("Old show times deleted successfully.")
    except Exception as e:
        logger.error(f"Error in delete_old_show_times: {e}")
        raise

@shared_task
def release_expired_locks():
    try:
        now = timezone.now()
        expired_book = Booking.objects.filter(
            is_locked=True,
            is_booked=False,
            lock_expires_at__lte=now
        )

        for booking in expired_book:
            booking.is_locked = False
            booking.locked_by = None
            booking.lock_expires_at = None
            booking.save()
        
        logger.info("Expired locks released successfully.")
    except Exception as e:
        logger.error(f"Error in release_expired_locks: {e}")
        raise
