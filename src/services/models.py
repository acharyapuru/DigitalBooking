from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Create your models here.
class Service(models.Model):
    SERVICE_CHOICES = (
        (_('Movies'), _('Movies')),
        (_('Flights'), _('Flights')),
        (_('Buses'), _('Buses')),
        (_('Cable Cars'), _('Cable Cars')),

    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Service Name"),
    )

    service_type = models.CharField(
        _("Service Type"),
        max_length=50,
        choices=SERVICE_CHOICES,
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name="Service Slug",
        unique=True,
        editable=False,
    )

    photo = models.ImageField(
        upload_to="services",
        verbose_name="Service Photo",
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.service_type)
        return super().save(*args, **kwargs)