from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Genre(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Category Name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Category Slug"),
        unique=True,
        editable=False,
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Movie Genre")
        verbose_name_plural = _("Movie Genres")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    

class Movie(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Movie Name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Movie Slug"),
        unique=True,
        editable=False,
    )

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name=_("Movie Genre"),
    )

    thumbnail = models.ImageField(
        upload_to="movies",
        verbose_name=_("Movie Thumbnail"),
    )

    language = models.CharField(
        max_length=50,
        verbose_name=_("Movie Language"),
    )

    casts = models.CharField(
        max_length=255,
        verbose_name=_("Movie Casts"),
    )

    director = models.CharField(
        max_length=255,
        verbose_name=_("Movie Director"),
    )

    duration = models.CharField(
        max_length=50,
        verbose_name=_("Movie Duration"),
    )

    release_date = models.DateField(
        verbose_name=_("Release Date"),
    )

    description = models.TextField(
        verbose_name=_("Movie Description"),
        null=True,
        blank=True,
    )


    trailer = models.FileField(
        upload_to="movies/trailers",
        verbose_name=_("Movie Trailer"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_shown = models.BooleanField(
        default=True,
        verbose_name=_("Is Shown"),
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Movie")
        verbose_name_plural = _("Movies")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    

    
class Theater(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Theater Name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Theater Slug"),
        unique=True,
        editable=False,
    )

    location = models.CharField(
        max_length=255,
        verbose_name=_("Theater Location"),
    )

    phone = models.CharField(
        max_length=20,
        verbose_name=_("Theater Phone"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Theater")
        verbose_name_plural = _("Theaters")


class ShowDay(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="show_days",
        verbose_name=_("Movie Name"),
    )

    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE,
        verbose_name=_("Theater Name"),
    )

    day = models.DateField(
        verbose_name=_("Show Day"),
    )

    is_trashed = models.BooleanField(
        default=False,
        verbose_name=_("Is Trashed"),
    )

    def __str__(self):
        return f"{self.movie.name} at {self.theater.name} on {self.day}"
    
    class Meta:
        verbose_name = _("Show Day")
        verbose_name_plural = _("Show Days")


class ShowTime(models.Model):
    show_day = models.ForeignKey(
        ShowDay,
        on_delete=models.CASCADE,
        related_name="show_times",
        verbose_name=_("Show Day"),
    )

    time = models.TimeField(
        verbose_name=_("Show Time"),
    )

    is_trashed = models.BooleanField(
        default=False,
        verbose_name=_("Is Trashed"),
    )

    class Meta:
        unique_together =  ['show_day', 'time']
        verbose_name = _("Show Time")
        verbose_name_plural = _("Show Times")

    def __str__(self):
        return f"{self.show_day.movie.name} at {self.time} on {self.show_day.day} at {self.show_day.theater.name}"


class SeatType(models.Model):
    name = models.CharField(
        _("Seat Type"),
        max_length=255,
    )

    price = models.PositiveIntegerField(
        _("Price"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Seat Type")
        verbose_name_plural = _("Seat Types")

class Seat(models.Model):
    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE,
        related_name="seats",
        verbose_name=_("Theater Name"),
    )

    seat_type = models.ForeignKey(
        SeatType,
        on_delete=models.CASCADE,
        verbose_name=_("Seat Type"),
        null=True,
    )

    row = models.CharField(
        _("Row"),
        max_length=1
    )

    number = models.PositiveIntegerField(
        _("Number"),
    )

    def __str__(self):
        return f"Row {self.row}, Seat {self.number} at {self.theater.name}"

    class Meta:
        unique_together = ["theater", "row", "number"]
        verbose_name = _("Seat")
        verbose_name_plural = _("Seats")


class Booking(models.Model):
    show_time = models.ForeignKey(
        ShowTime,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Show Time"),
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Seat"),
    )

    user = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("User"),
    )

    is_booked = models.BooleanField(
        _("Is Booked"),
        default=False,
    )

    is_locked = models.BooleanField(
        _("Is Locked"),
        default=False,
    )

    locked_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="locked_bookings",
        verbose_name=_("Locked By"),
    )

    lock_expires_at = models.DateTimeField(
        _("Lock Expires At"),
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["show_time", "seat"]
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

