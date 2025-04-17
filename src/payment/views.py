from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.generics import ListAPIView
from django.views import View
from .models import PaymentMethod, MovieTicketPayment
from .serializers import PaymentMethodSerializer
from django.http import JsonResponse
from django.conf import settings
from . import utils
import json
import io
from collections import defaultdict
from django.db import transaction
from movie.models import Seat, ShowTime, Booking
import requests
from django.template.loader import render_to_string
from weasyprint import HTML
from offer.models import PromoCode, Transaction
from django.contrib.contenttypes.models import ContentType
from offer import utils as offer_utils
# Create your views here.

class PaymentMethodListAPIView(ListAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class PaymentView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.body.decode('utf-8')
        data = json.loads(data)


        payment_method = data.get('payment_method')
        movie_slug = data.get('movie_slug')
        theater_slug = data.get('theater_slug')
        show_time = data.get('show_time')
        seat_ids = data.get('seat_ids')
        seat_numbers = data.get('seat_numbers')
        promo_code = data.get('promo_code')
        user = request.user


        try:
            utils.validate_payment_data(
                payment_method=payment_method,
                movie_slug=movie_slug,
                theater_slug=theater_slug,
                show_time=show_time,
                seat_ids=seat_ids,
                seat_numbers=seat_numbers,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        payment_method = PaymentMethod.objects.get(slug=payment_method)
        show_time = ShowTime.objects.get(id=show_time)
        movie = show_time.show_day.movie

        if promo_code:
           promoCode = self.validate_promo_code(promo_code, user)


        if payment_method.name == 'esewa':
            pass
        elif payment_method.name == 'khalti':
            seats = Seat.objects.filter(id__in=seat_ids)
            total_amount = sum([seat.seat_type.price for seat in seats])
            payable_amount = total_amount
            discount = 0
            if promoCode[0]:
                discount = promoCode[1].get_discounted_value(total_amount)
                payable_amount = total_amount - discount
                offer_utils.redeem_promo_code(promoCode[1], user.profile)

            txn = MovieTicketPayment.objects.create(
                user=user,
                payment_method=payment_method,
                amount=total_amount,
                movie=movie,
                show_time=show_time,
                payable_amount=payable_amount,
                discount=discount 
            )
            txn.seats.add(*seats)

            try:
                response_data = self.initialize_khalti_payment(payable_amount, user, txn)
                payment_url = response_data.get('payment_url')
                if not payment_url:
                    raise ValueError("Failed to retrieve payment URL from Khalti.")
                
                # Return the payment URL in the JSON response
                return JsonResponse({"payment_url": payment_url})
            except Exception as e:
                # Provide `data` parameter as a dictionary with error information
                return JsonResponse({"error": f"Khalti payment initiation failed: {str(e)}"}, status=500)


        return JsonResponse({"message": "Payment processed successfully"})
    
    def validate_promo_code(self, promo_code, user):
        from offer.utils import RuleValidator
        try:
            promoCode = PromoCode.objects.get(code__iexact=promo_code)
            
            allowed_users_validation = RuleValidator.validate_allowed_users(user, promoCode.conditions.allowed_users)
            if not allowed_users_validation[0]:
                raise ValueError(allowed_users_validation[1])
            
            current_uses = promoCode.redemption_count
            promo_content_type = ContentType.objects.get_for_model(PromoCode)
            user_uses = Transaction.objects.filter(
                user=user.profile,
                entity_content_type=promo_content_type,
                entity_object_id=promoCode.id,
            ).count()
            max_uses_validation = RuleValidator.validate_max_uses(promoCode.conditions.max_uses, current_uses, user_uses)
            if not max_uses_validation[0]:
                raise ValueError(max_uses_validation[1])
            
            validity_validation = RuleValidator.validate_validity(promoCode.conditions.validity)
            if not validity_validation[0]:
                raise ValueError(validity_validation[1])
            
            custom_rules_validation = RuleValidator.validate_custom_rules(promoCode.conditions.custom_rules.all(), {})

            return True, promoCode
        
        except Exception as e:
            raise ValueError("Invalid promo code", e)

    def initialize_khalti_payment(self, amount, user, txn):
        khalti_url = settings.KHALTI_INIT_URL
        khalti_secret_key = settings.KHALTI_LIVE_SECRET_KEY
        amount = int(amount * 100)  # Convert amount to paisa

        payload = json.dumps({
            "return_url": settings.KHALTI_RETURN_URL,
            "website_url": "http://127.0.0.1:8000",
            "amount": amount,
            "purchase_order_id": f"{txn.uuid}",
            "purchase_order_name": "Movie Ticket",
            "customer_info": {
                "name": user.email,
                "discount": txn.discount,
            },
            "merchant_idx": f"{txn.uuid}",
        })
        headers = {
            'Authorization': f'Key {khalti_secret_key}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", khalti_url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status() 


class KhaltiStatusView(View):
    def get(self, request, *args, **kwargs):
        pidx = request.GET.get('pidx')
        idx = request.GET.get('idx')

        khalti_verify_url = settings.KHALTI_VERIFY_URL

        try:
            payload = json.dumps({
                'pidx': pidx
            })

            headers = {
                'Authorization': f'key {settings.KHALTI_LIVE_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", khalti_verify_url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status') == 'Completed':

                    with transaction.atomic():

                        txn = MovieTicketPayment.objects.get(uuid=idx)
                        txn.is_paid  = True
                        txn.save()

                        seats = txn.seats.all()
                        for seat in seats:
                            booking = get_object_or_404(
                                Booking, show_time=txn.show_time, seat=seat
                            )
                            booking.is_booked = True
                            booking.is_locked = False
                            booking.save()


                context = {
                    'txn_id': idx,
                    'total_amount': response_data.get('total_amount')/100,
                    'status': response_data.get('status'),
                }
            else:
                response.raise_for_status()
        except Exception as e:
            print(e)

        return render(request, 'payment/payment_status.html', context)


def generate_movie_ticket_pdf(request, txn_id):
    txn = get_object_or_404(MovieTicketPayment, uuid=txn_id)

    movie_thumbnail_url = request.build_absolute_uri(txn.movie.thumbnail.url)
    qr_code_base64 = utils.generate_movie_qr(txn_id)

    # Initialize seat information structure
    seat_info = defaultdict(lambda: {"quantity": 0, "price_per_ticket": 0, "total_price": 0})
    
    for seat in txn.seats.all():
        seat_type = seat.seat_type.name  # e.g., 'Platinum' or 'Premium'
        seat_price = seat.seat_type.price  # Price for each seat
        seat_info[seat_type]["quantity"] += 1
        seat_info[seat_type]["price_per_ticket"] = seat_price
        seat_info[seat_type]["total_price"] = seat_info[seat_type]["quantity"] * seat_price



    # Format seats as "A1, A2, B3" etc.
    formatted_seats = [f"{seat.row}{seat.number}" for seat in txn.seats.all()]
    formatted_seats_string = ", ".join(formatted_seats)

    context = {
        'theater': txn.show_time.show_day.theater.name,
        'theater_address': txn.show_time.show_day.theater.location,
        'movie_name': txn.movie.name,
        'movie_description': txn.movie.description,
        'movie_duration': txn.movie.duration,
        'movie_thumbnail_url': movie_thumbnail_url,
        'show_time': txn.show_time.time,
        'show_date': txn.show_time.show_day.day,
        'seats': formatted_seats_string,
        'no_of_seats': txn.seats.count(),
        'transaction_id': txn_id,
        'total_amount': (txn.amount/100),
        'transaction_date': txn.created_at,
        'ticket_type': 'Movie Ticket',
        'transaction_method': txn.payment_method.name,
        'qr_code_base64': qr_code_base64,
        'seat_info': dict(seat_info),
    }


    html_string = render_to_string('payment/movie_ticket.html', context)
    html = HTML(string=html_string)

    pdf_file = io.BytesIO()
    html.write_pdf(target=pdf_file)

    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="movie_ticket_{txn_id}.pdf"'
    
    return response
    

