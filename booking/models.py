from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    title = models.CharField(max_length=100, unique=True)
    capacity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    '''class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ["number_room"]'''


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booking")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_confirmed = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.start_date > self.end_date:
            raise ValidationError(_("LSLS"))

        if Booking.objects.filter(location=self.location).exclude(pk=self.pk).filter(
            Q(start_date__lte=self.end_date) & Q(end_date__gte=self.start_date)
        ).exists():
            raise ValidationError(_("erre"))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)