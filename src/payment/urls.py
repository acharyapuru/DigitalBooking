from django.urls import path
from . import views

app_name='payment'

urlpatterns = [
    path('payment-methods/', views.PaymentMethodListAPIView.as_view(), name='payment-methods'),
    path('process-payment/', views.PaymentView.as_view(), name='payment'),
    path('khalti/status/', views.KhaltiStatusView.as_view(), name='khalti-status'),
    path('print-ticket/<uuid:txn_id>/', views.generate_movie_ticket_pdf, name='print-ticket'),
]
