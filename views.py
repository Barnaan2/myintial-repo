from django.shortcuts import render, redirect
from system_admin.models import Hotel
from .models import BookingRequest, RequestedRoom, Review
from .forms import ReviewForm
from hotel.models import Room, PaymentInformation
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    form = ReviewForm()
    q = None
    hotel = Hotel.objects.all()
    hotel_list = Paginator(hotel, 15)
    page_number = request.GET.get('page')
    hotels = hotel_list.get_page(page_number)
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
        hotels = Hotel.objects.filter(
            Q(city__name__icontains=q) |
            Q(name__icontains=q))
    if request.method == "POST":
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'you have added new review ')
                return redirect('index')
            else:
                messages.error(request, 'terror occurred')
        else:
            messages.error(request, 'login to give a feedback')
            return redirect('login')
    context = {'hotels': hotels, 'form': form}
    return render(request, 'index.html', context)


def selected_hotel(request, q):
    hotel = Hotel.objects.get(id=q)
    rooms = Room.objects.filter(hotel=hotel)
    context = {'hotel': hotel, 'rooms': rooms}
    if request.method == "POST":
        if request.user.is_anonymous:
            messages.error(request, 'please login or register to book')
            return redirect('login')
        else:
            booking_request = BookingRequest.create()
            # the front end will send the room_id and the no_rooms both are  an array
            for room_id in request.POST['room_id']:
                room = Room.objects.get(id=room_id)
                booking_request.room.add(room, through_defaults={'number_of_room': 1})
    return render(request, '', context)


def selected_room(request, q):
    room = Room.objects.get(id=q)
    context = {'room': room}
    return render(request, '', context)


# this should work if the user role is a customer
def my_booking(request):
    bookings = BookingRequest.objects.filter(user=request.user)
    context = {'bookings': bookings}
    return render(request, '', context)


def pay(request):
    q = None
    if request.GET.get('q') is not None:
        q = request.GET.get('q')
        booking_request = BookingRequest.objects.get(id=q)
        if booking_request.status != "pay":
            messages.error(request, 'the booking cannot accept payment ')
            return redirect('booking')
        room = booking_request.room.all().first()
        hotel = room.hotel
        payment_information = PaymentInformation.objects.filter(hotel=hotel)
        # requested_rooms = RequestedRoom.objects.filter(booking_request=booking_request).first()
    context = {'payment_information': payment_information}
    if request.method == "POST":
        # here the posted value should fill the bill information
        pass
    return render(request, '', context)


def edit_review(request, q):
    review = Review.objects.get(id=q)
    form = ReviewForm(instance=review)
    if request.user == review.reviewer:
        if request.method == "POST":
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
            else:
                messages.error(request, 'there is an error in your input')
    else:
        return redirect('index')
    context = {'form': form}
    return render(request, '', context)


def delete_review(request, q):
    review = Review.objects.get(id=q)
    if request.user == review.reviewer:
        if request.method == "POST":
            review.delete()
            messages.error(request, 'you have removed the review')
            return redirect('index')
    else:
        return redirect('index')
    return render(request,'',{'review':review})
