from rest_framework import serializers
from .models import PaymentMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

# class PaymentProcessSerializer(serializers.Serializer):
#     payment_method = serializers.CharField()
#     movie_slug = serializers.CharField()
#     theater_slug = serializers.CharField()
#     show_time = serializers.CharField()
#     seat_ids = serializers.ListField(child=serializers.CharField())
#     seat_numbers = serializers.ListField(child=serializers.CharField())

#     class Meta:
#         fields = ['payment_method', 'movie_slug', 'theater_slug', 'show_time', 'seat_ids', 'seat_numbers']
#         read_only_fields = ['payment_method', 'movie_slug', 'theater_slug', 'show_time', 'seat_ids', 'seat_numbers']

#     def validate(self, data):
#         print('data', data)
#         payment_method = data.get('payment_method')
#         movie_slug = data.get('movie_slug')
#         theater_slug = data.get('theater_slug')
#         show_time = data.get('show_time')
#         seats = data.get('seat_ids')
#         seat_numbers = data.get('seat_numbers')

#         if not payment_method:
#             raise serializers.ValidationError("Payment method is required")
#         if not movie_slug:
#             raise serializers.ValidationError("Movie is required")
#         if not theater_slug:
#             raise serializers.ValidationError("Theater is required")
#         if not show_time:
#             raise serializers.ValidationError("Show time is required")
#         if not seats:
#             raise serializers.ValidationError("Seats are required")
#         if not seat_numbers:
#             raise serializers.ValidationError("Seat numbers are required")

#         return data