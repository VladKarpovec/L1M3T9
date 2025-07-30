from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import os
from uuid import uuid4


def booking_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('booking_photos', str(instance.pk), filename)


class Location(models.Model):
    title = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='location_images/', null=True, blank=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(User, related_name="bookings", on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name="bookings", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)
    token = models.CharField(max_length=16)

    def clean(self):
        super().clean()
        if self.start_date > self.end_date:
            raise ValidationError(_("Дата початку не можу бути пізніше дати кінця"))

        if Booking.objects.filter(location=self.location).exclude(pk=self.pk).filter(
            Q(start_date__lte=self.end_date) & Q(end_date__gte=self.start_date)
        ).exists():
            raise ValidationError(_(f"Ці дати вже зайняті для локації {self.location.title}"))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)