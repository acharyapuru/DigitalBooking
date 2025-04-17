from rest_framework import serializers
from .models import Seat, Booking

class SeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.BooleanField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='seat_type.price')
    seat_number = serializers.SerializerMethodField()
    class Meta:
        model = Seat
        fields = ['id','row', 'number', 'is_booked', 'is_locked', 'price', 'seat_number']

    def get_seat_number(self, obj):
        return f"{obj.row}{obj.number}"

class BookingSerializer(serializers.ModelSerializer):
    seat_id = serializers.SerializerMethodField()
    class Meta:
        model = Booking
        fields = ['seat_id', 'show_time', 'is_locked', 'is_booked', 'locked_by']

    def get_seat_id(self, obj):
        return obj.seat.id

