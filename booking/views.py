from django.shortcuts import render, redirect
from .models import MeetingRoom, Booking
from .forms import BookingForm
import datetime

def booking_list(request):
    today = datetime.date.today()
    bookings = Booking.objects.filter(start_time__date=today).order_by('start_time')
    context = {'bookings': bookings, 'today': today}
    return render(request, 'booking/booking_list.html', context)

def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    context = {'form': form}
    return render(request, 'booking/book.html', context)