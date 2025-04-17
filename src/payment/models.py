from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.conf import settings
from movie.models import Movie, ShowTime, Seat

# Create your models here.

class PaymentMethod(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Payment Method"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Payment Method Slug"),
        unique=True,
        editable=False,
    )

    logo = models.ImageField(
        upload_to="payment_methods",
        verbose_name=_("Payment Method Logo"),
    )

    def __str__(self):
        return self.name.upper()
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")


class MovieTicketPayment(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        verbose_name=_("Payment Method"),
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        verbose_name=_("Movie"),
        null=True,
        blank=True,
    )

    show_time = models.ForeignKey(
        ShowTime,
        on_delete=models.CASCADE,
        verbose_name=_("Show Time")
    )

    seats = models.ManyToManyField(
        Seat,
        verbose_name=_("Seats"),
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name=_("Is Paid"),
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Discount"),
        default=0.0,
    )

    payable_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Payable Amount"),
        default=0.0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.payment_method}"
    
    class Meta:
        verbose_name = _("Movie Ticket Payment")
        verbose_name_plural = _("Movie Ticket Payments")
