from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from config import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from django.utils.dateparse import parse_datetime
from django.http import HttpResponse
from booking.models import Location, Booking
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.urls import reverse

def home(request):
    context = {
        "render_string": "Hello, world!"
    }
    return render(request, 'booking/home.html', context=context)

def reservation_list(request):
    reservation_list = Location.objects.all()
    context = {
        "reservation_list": reservation_list,
    }
    return render(request, 'booking/reservation_list.html', context=context)

@login_required
def book_location(request):
    if request.method == "POST":
        location_title = request.POST.get("location-title")
        start_time_str = request.POST.get("start-time")
        end_time_str = request.POST.get("end-time")

        try:
            location = Location.objects.get(title=location_title)
        except Location.DoesNotExist:
            return HttpResponse("This location doesn't exist", status=404)

        start_date = parse_datetime(start_time_str)
        end_date = parse_datetime(end_time_str)

        if not start_date or not end_date:
            messages.error(request, "❌ Невірна дата")
            return render(request, "booking/booking_form.html", {
                "location_title": location_title
            })

        if end_date <= start_date:
            messages.error(request, "❌ Дата завершення має бути пізнішою за дату початку.")
            return render(request, "booking/booking_form.html", {
                "location_title": location_title
            })

        if start_date.date() < datetime.now().date():
            messages.error(request, "❌ Неможливо забронювати на минулу дату.")
            return render(request, "booking/booking_form.html", {
                "location_title": location_title
            })

        overlapping = Booking.objects.filter(
            location=location,
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()

        if overlapping:
            messages.error(request, "❌ Локація вже заброньована на ці дати.")
            return render(request, "booking/booking_form.html", {
                "location_title": location_title
            })

        token = get_random_string(length=16)
        booking = Booking.objects.create(
            user=request.user,
            location=location,
            start_date=start_date,
            end_date=end_date,
            token=token
        )

        url = f"{request.scheme}://{request.get_host()}{reverse('main:activation', args=[booking.pk, token])}"

        send_mail(
            subject="🔔 Підтвердження бронювання",
            message=f"Будь ласка, підтвердіть своє бронювання за посиланням: {url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            html_message=render_to_string(
                "booking/email/confirmation_email.html",
                {
                    "booking": booking,
                    "user": request.user,
                    "confirmation_url": url,
                    "site_name": "BookingHub"
                }
            ))

        messages.success(request,
                         "На вашу пошту надіслано лист для підтвердження бронювання. Будь ласка, підтвердіть його.")
        return redirect("main:booking_details", pk=booking.id)
    if request.method == "GET":
        location_title = request.GET.get("location", "")
        return render(request, "booking/booking_form.html", {
            "location_title": location_title
        })
    return render(request, "booking/booking_form.html")


@login_required
def booking_details(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, "booking/booking_details.html", {"booking": booking})


@login_required
def profile_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "booking/profile_view.html", {"bookings": bookings})


@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.is_confirmed:
        messages.error(request, "Підтверджене бронювання не можна видалити.")
    else:
        booking.delete()
        messages.success(request, "Бронювання успішно видалено.")

    return redirect('main:profile_view')

def activation_view(request, booking_id, token):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.token == token:
        booking.is_confirmed = True
        booking.save()
    return redirect("main:home")
