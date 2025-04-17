from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import BulkSeatCreation, BulkShowDays, BulkShowTime
from django.contrib import messages
import logging
from datetime import datetime
from .models import Genre, Movie, ShowDay, ShowTime, Seat, Theater, Booking, SeatType

# Register your models here.

logger = logging.getLogger('django')

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    actions = ['bulk_create_seats_action']

    def bulk_create_seats(self, request):
        if 'apply' in request.POST:
            form = BulkSeatCreation(request.POST)
            if form.is_valid():
                theater = form.cleaned_data['theater']  # Get selected theater
                start_row = form.cleaned_data['start_row']
                end_row = form.cleaned_data['end_row']
                seats_per_row = form.cleaned_data['seats_per_row']

                start_row_ord = ord(start_row.upper())  # Ensure uppercase
                end_row_ord = ord(end_row.upper())

                new_seats = []
                for row_ord in range(start_row_ord, end_row_ord + 1):
                    row_letter = chr(row_ord)
                    for seat_number in range(1, seats_per_row + 1):
                        new_seats.append(Seat(theater=theater, row=row_letter, number=seat_number))

                # Create seats in bulk
                Seat.objects.bulk_create(new_seats)
                logger.info(f"{len(new_seats)} seats have been created")
                messages.success(request, f"{len(new_seats)} seats have been added to {theater}.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkSeatCreation()

        context = {'form': form}
        return render(request, "admin/add_seats.html", context)
    
    @admin.action(description='Bulk create seats')
    def bulk_create_seats_action(self, request, queryset):
        return HttpResponseRedirect('bulk_create_seats/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk_create_seats/', self.admin_site.admin_view(self.bulk_create_seats), name='bulk_create_seats'),
        ]
        return custom_urls + urls

@admin.register(ShowDay)
class ShowDayAdmin(admin.ModelAdmin):
    list_display = ("movie", "theater", "day", "get_show_day")
    list_filter = ("movie", "theater", "day")

    change_list_template = "admin/change_list.html"

    @admin.display(description='Show Day')
    def get_show_day(self, obj):
        return obj.day.strftime("%A")

    def bulk_create_show_day(self, request):
        form = None
        if request.method == 'POST':
            form = BulkShowDays(request.POST)
            if form.is_valid():
                movies = form.cleaned_data['movies']
                theaters = form.cleaned_data['theaters']
                show_date = form.cleaned_data['show_date']

                new_show_days = []
                for movie in movies:
                    for theater in theaters:
                        new_show_days.append(ShowDay(movie=movie, theater=theater, day=show_date))
                
                ShowDay.objects.bulk_create(new_show_days)
                self.message_user(request, f"{len(new_show_days)} show days have been created.")
                return redirect('..')
        else:
            form = BulkShowDays()
        
        context = {'form': form}
        return render(request, "admin/add_show_day.html", context)
    
    def get_urls(self):
        urls= super().get_urls()
        custom_urls = [
            path(
                'bulk_create_show_day/',
                self.admin_site.admin_view(self.bulk_create_show_day),
                name='bulk_create_show_day'
            )
        ]
        return custom_urls + urls


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ("show_day", "time")
    list_filter = ("show_day__movie", "show_day__theater", "show_day__day")


    def bulk_create_show_time(self, request):
        form = None
        if request.method == 'POST':
            form = BulkShowTime(request.POST)
            if form.is_valid():
                show_day = form.cleaned_data['show_day']
                show_times = form.cleaned_data['show_times'].split(',')

                new_show_times = []
                for time in show_times:
                    new_show_times.append(ShowTime(show_day=show_day, time=datetime.strptime(time.strip(), "%H:%M").time()))
                
                ShowTime.objects.bulk_create(new_show_times)
                self.message_user(request, f"{len(new_show_times)} show times have been created.")
                return redirect('..')
        else:
            form = BulkShowTime()

        context = {'form': form}
        return render(request, "admin/add_show_time.html", context)
    
    def get_urls(self):
        urls= super().get_urls()
        custom_urls = [
            path('bulk_create_show_time/', self.admin_site.admin_view(
                self.bulk_create_show_time), name='bulk_create_show_time'
            )
        ]
        return custom_urls + urls

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("theater", "row", "number", "seat_type")
    list_filter   = ("theater",)
    actions = ['bulk_create_seats']
    list_editable = ("seat_type",)

    
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("name","slug", "genre", "language", "thumbnail")
    list_filter = ("genre", "language")
    search_fields = ("name", "genre", "language")
    list_per_page = 10

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("show_time", "seat","theater","is_booked")
    list_filter = ("show_time","show_time__show_day", "seat", "is_booked", "seat__theater", "show_time__show_day__movie")
    search_fields = ("show_time", "seat", "is_booked")
    list_per_page = 10

    @admin.display(description='Theater')
    def theater(self, obj):
        return obj.seat.theater

@admin.register(SeatType)
class SeatTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
