from django.contrib import admin
from .models import PaymentMethod, MovieTicketPayment

# Register your models here.

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    readonly_fields = ("slug",)

@admin.register(MovieTicketPayment)
class MovieTicketPaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_method", "movie", "amount", "is_paid")
    search_fields = ("user__username",)
    list_filter = ("payment_method",)
    ordering = ("-created_at",)