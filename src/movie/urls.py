from django.urls import path
from . import views

app_name = 'movie'

urlpatterns = [
    path('', views.MovieView.as_view(), name='movies'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('show_days/<slug:theater_slug>/<slug:movie_slug>/', views.TheaterView.as_view(), name='show_days'),
    path('get_show_times/<int:show_day>/', views.ShowTimeView.as_view(), name='get_show_times'),
    path('<slug:movie>/<slug:theater>/tickets/<str:show_time>/', views.BookingView.as_view(), name='booking'),
]