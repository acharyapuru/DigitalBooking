from django.shortcuts import render
from django.views import View
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from collections import defaultdict
from django.db.models import Count, Case, When, Value, FloatField, F, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Cast
from .models import Movie, Theater, ShowDay, ShowTime, Seat

# Create your views here.

class MovieView(View):
    def get(self, request):
        if request.GET.get('q'):
            query = request.GET.get('q')
            now_showing_movies = Movie.objects.filter(name__icontains=query, is_shown=True).order_by('-created_at')
            upcomming_movies = Movie.objects.filter(name__icontains=query, release_date__gt=timezone.now().today())
            context = {
                "now_showing_movies": now_showing_movies,
                "upcomming_movies": upcomming_movies
            }
            return render(request, 'movie/movies.html', context)
        else:
            now_showing_movies = Movie.objects.filter(is_shown=True).order_by('-created_at')
            upcomming_movies = Movie.objects.filter(release_date__gt=timezone.now().today())
            context = {
                "now_showing_movies": now_showing_movies,
                "upcomming_movies": upcomming_movies
            }
            return render(request, 'movie/movies.html', context)
    

class MovieDetailView(View):
    def get(self, request, slug):
        movie = Movie.objects.get(slug=slug)
        theaters = Theater.objects.all()
        context = {
            "movie": movie,
            "theaters": theaters,
            "base_url": settings.BASE_URL
        }
        return render(request, 'movie/movie_detail.html', context)

class TheaterView(View):
    def get(self, request, theater_slug, movie_slug):
        today = timezone.now().today()
        show_days = ShowDay.objects.filter(theater__slug=theater_slug, movie__slug=movie_slug).filter(day__gte=today).values('id','day')
        return JsonResponse(list(show_days), safe=False)
    

class ShowTimeView(View):
    def get(self, request, show_day):
        show_times = ShowTime.objects.filter(
            show_day=show_day
        ).annotate(
            total_seats=Count('show_day__theater__seats',distinct=True),
            booked_seats=Count('bookings', filter=Q(bookings__is_booked=True), distinct=True)
        ).annotate(
            occupancy_percentage=Cast(F('booked_seats'), FloatField()) / Cast(F('total_seats'), FloatField()) * 100,
            status=Case(
                When(occupancy_percentage=100, then=Value('no-available')),
                When(occupancy_percentage__gte=80, then=Value('fast-filling')),
                default=Value('available'),
            )
        )

        show_times_data = list(show_times.values('id', 'time', 'status', 'occupancy_percentage', 'total_seats', 'booked_seats'))
        return JsonResponse(show_times_data, safe=False)

def grout_seats_by_row(seats):
    rows = defaultdict(list)
    for seat in seats:
        rows[seat.row].append(seat)
    return rows

class BookingView(LoginRequiredMixin, View):
    login_url = 'user:login'
    redirect_field_name = 'next'
    def get(self, request, movie, theater, show_time):
        show_time = ShowTime.objects.get(id=show_time)
        seats =  Seat.objects.filter(theater__slug=theater).order_by('row', 'number')
        seats_by_row  = dict(grout_seats_by_row(seats))
        context = {
            "show_time": show_time,
            "theater": theater,
            "movie": show_time.show_day.movie,
            "seats_by_row": seats_by_row,
            "current_user": request.user.id
        }
        return render(request, 'movie/booking.html', context)