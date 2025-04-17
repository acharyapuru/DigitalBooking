from django.core.exceptions import ValidationError
import qrcode
from io import BytesIO
import base64

def validate_payment_data(**kwargs):
    payment_method = kwargs.get('payment_method')
    movie_slug = kwargs.get('movie_slug')
    theater_slug = kwargs.get('theater_slug')
    show_time = kwargs.get('show_time')
    seat_ids = kwargs.get('seat_ids')
    seat_numbers = kwargs.get('seat_numbers')

    if not payment_method:
        raise ValidationError("Payment method is required")
    if not movie_slug:
        raise ValidationError("Movie is required")
    if not theater_slug:
        raise ValidationError("Theater is required")
    if not show_time:
        raise ValidationError("Show time is required")
    if not seat_ids:
        raise ValidationError("Seats are required")
    if not seat_numbers:
        raise ValidationError("Seat numbers are required")
    
    return kwargs


def generate_pdf():
    pass

def generate_movie_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

     # Convert image to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return qr_base64