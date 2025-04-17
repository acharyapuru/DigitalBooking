from django.contrib.admin import ModelAdmin
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from .models import Transaction, PromoCode

def reset_coupon_uses(modeladmin, request, queryset):
    for coupon_user in queryset:
        coupon_user.times_used = 0
        coupon_user.save()

    ModelAdmin.message_user(modeladmin, request, 'Coupon uses reset successfully')


def delete_expired_coupons(modeladmin, request, queryset):
    count = 0
    for coupon in queryset:
        expiration_date = coupon.ruleset.validity.expiration_date
        if expiration_date < timezone.now():
            coupon.delete()
            count += 1

    ModelAdmin.message_user(modeladmin, request, '{0} expired coupons deleted successfully'.format(count))

reset_coupon_uses.short_description = 'Reset selected coupons uses'
delete_expired_coupons.short_description = 'Delete expired coupons'


class RuleValidator:
    @staticmethod
    def validate_allowed_users(user, allowed_user_rule):
        if allowed_user_rule.all_users:
            return True, "User is allowed"
        
        if user in allowed_user_rule.user.all():
            return True, "User is allowed"
        
        return False, "User is not allowed"
        
    @staticmethod
    def validate_max_uses(max_uses_rule, current_uses, user_uses):
        if max_uses_rule.is_infinite:
            return True, "Coupon is valid"
        
        if current_uses >= max_uses_rule.max_uses:
            return False, "Coupon has reached maximum uses"
        
        if user_uses >= max_uses_rule.uses_per_user:
            return False, "User has reached maximum uses"
        
        return True, "Usage is within limits"
    
    @staticmethod
    def validate_validity(validity_rule):
        if not validity_rule.is_active:
            return False, "Coupon is not active"
        
        if validity_rule.expiration_date < timezone.now():
            return False, "Coupon has expired"
        
        return True, "Coupon is valid"
    
    @staticmethod
    def validate_custom_rules(custom_rules, params):
        for rule in custom_rules:
            rule_type = rule.rule_type
            if rule_type == "min_purchase":
                if params.get("total_amount") < rule.params.get("minimum_purchase"):
                    return False, f"Minimum purchase amount does not meet the minimum of {rule.params.get('minimum_purchase')}"
        return True, "Custom rules are valid"


def redeem_promo_code(promo_code, user):
    try:
        promo_code_entity = ContentType.objects.get_for_model(PromoCode)
        txn = Transaction.objects.create(
            user=user,
            entity_content_type=promo_code_entity,
            entity_object_id=promo_code.id,
            action="redeem",
        )
        promo_code.redemption_count += 1
        promo_code.save()
        return txn
    except Exception as e:
        raise ValidationError(e)