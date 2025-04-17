from django import forms
from .models import Theater, Movie, ShowDay, ShowTime

class BulkSeatCreation(forms.Form):
    theater = forms.ModelChoiceField(
        queryset=Theater.objects.all(),
        empty_label="Select a Theater",
    )

    start_row = forms.CharField(
        max_length=1,
        help_text="Enter the starting row letter e.g. A",
    )

    end_row = forms.CharField(
        max_length=1,
        help_text="Enter the ending row letter e.g. Z",
    )

    seats_per_row = forms.IntegerField(
        help_text="Enter the number of seats per row",
    )

class BulkShowDays(forms.Form):
    movies = forms.ModelMultipleChoiceField(
        queryset=Movie.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Movies",
    )

    theaters = forms.ModelMultipleChoiceField(
        queryset=Theater.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Theaters",
    )

    show_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Show Date",
        help_text="Enter the date of the show",
    )


class BulkShowTime(forms.Form):
    show_day = forms.ModelChoiceField(
        queryset=ShowDay.objects.all(),
        empty_label="Select a Show Day",
    )

    show_times = forms.CharField(
        help_text="Enter show times separated by comma e.g. 10:00 AM, 1:00 PM",
    )

