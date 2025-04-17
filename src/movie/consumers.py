import json
from channels import exceptions
from channels.db import database_sync_to_async
from collections import defaultdict
from django.db.models import OuterRef, Exists
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Seat, Booking, ShowTime, Theater, Movie
from .serializers import SeatSerializer, BookingSerializer

def group_seats_by_row(seats):
    rows = defaultdict(list)
    for seat in seats:
        rows[seat['row']].append(seat)
    return rows



class MovieConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()

        self.movie = self.scope['url_route']['kwargs']['movie']
        self.theater = self.scope['url_route']['kwargs']['theater']
        self.show_time = self.scope['url_route']['kwargs']['show_time']

        self.room_group_name = f'{self.movie}_{self.theater}_{self.show_time}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.seats = await self.get_seats(self.theater, self.show_time)

        await self.send_group(self.room_group_name, 'movie.seats', self.seats)



    async def disconnect(self, close_code):
        raise exceptions.StopConsumer()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        data_source = data.get('source')

        if data_source == 'booking':
            pass
        elif data_source == 'lock':
           result = await self.handle_lock(data, self.user)
           await self.send_group(self.room_group_name, 'movie.seat_update', result)
        elif data_source == 'unlock':
            result = await self.handle_unlock(data, self.user)
            print(result)
            await self.send_group(self.room_group_name, 'movie.seat_update', result)
    

    async def send_group(self, group_name, source, data):
        response = {
            "type": "broadcast.group",
            "source": source,
            "data": data
        }

        await self.channel_layer.group_send(
            group_name,
            response
        )
    
    async def broadcast_group(self, event):
        await self.send(
            text_data=json.dumps({
                'source': event.get('source'),
                'data': event.get('data')
            })
        )


    @database_sync_to_async
    def get_seats(self, theater, show_time):
        seats = Seat.objects.filter(theater__slug=theater).annotate(
            is_booked=Exists(
                Booking.objects.filter(
                    seat=OuterRef('pk'),
                    show_time=show_time,
                    is_booked=True
                )
            ),
            is_locked=Exists(
                Booking.objects.filter(
                    seat=OuterRef('pk'),
                    show_time=show_time,
                    is_locked=True
                )
            )
        ).order_by('row', 'number')
        serializer = SeatSerializer(seats, many=True)
        seats_by_row = group_seats_by_row(serializer.data)
        return seats_by_row
    
    @database_sync_to_async
    def handle_lock(self, data, user):
        seat_id = data.get('seat_id')
        show_time_id = data.get('show_time')
        seat = Seat.objects.get(id=seat_id)
        show_time = ShowTime.objects.get(id=show_time_id)
        try:
            booking, created = Booking.objects.get_or_create(
                seat=seat,
                show_time=show_time,
                is_locked=False,
                is_booked=False
            )
            booking.is_locked = True
            booking.locked_by = user
            booking.lock_expires_at = timezone.now() + timezone.timedelta(minutes=5)
            booking.save()
            serialized_seat = BookingSerializer(
                booking
            )
            print(serialized_seat.data)
            return serialized_seat.data
        except Exception as e:
            print('exception',e)
            return {"error": "Seat is already locked"}
    
    @database_sync_to_async
    def handle_unlock(self, data, user):
        seat_id = data.get('seat_id')
        show_time_id = data.get('show_time')
        seat = Seat.objects.get(id=seat_id)
        show_time = ShowTime.objects.get(id=show_time_id)
        try:
            booking = Booking.objects.get(
                seat=seat,
                show_time=show_time,
                is_locked=True,
                locked_by=user
            )
            booking.is_locked = False
            booking.locked_by = None
            booking.lock_expires_at = None
            booking.save()
            serialized_seat = BookingSerializer(
                booking
            )
            return serialized_seat.data
        
        except Exception as e:
            print('exception',e)
            return {"error": "Seat is already unlocked"}
        
    @database_sync_to_async  
    def unlock_seats(self):
        seats = Booking.objects.filter(
            show_time=self.show_time,
            is_locked=True,
            is_booked=False,
            locked_by=self.user
        )
        seats.update(is_locked=False, locked_by=None, lock_expires_at=None)
