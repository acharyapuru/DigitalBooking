from django.contrib import admin
from .models import (
    AllowedUserRule, MaxUsesRule, 
    ValidityRule, Discount, RuleSet, 
    Coupon, CustomRule, UserCoupon, 
    Gems, Points, RewardTermsAndConditions, 
    UserRewardWallet, PromoCode, Transaction
)

from .utils import reset_coupon_uses, delete_expired_coupons
# Register your models here.

@admin.register(CustomRule)
class CustomRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_type', 'rule_name', 'params')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'times_used', 'created_at', 'ruleset')
    actions = [delete_expired_coupons]

admin.site.register(Discount)

@admin.register(RuleSet)
class RulesetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'allowed_users', 'max_uses', 'validity')

@admin.register(AllowedUserRule)
class AllowedUserRuleAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}

@admin.register(MaxUsesRule)   
class MaxUsesRuleAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}

@admin.register(ValidityRule)
class ValidityRuleAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


admin.site.register(Gems)
admin.site.register(Points)
admin.site.register(RewardTermsAndConditions)
admin.site.register(UserRewardWallet)
admin.site.register(UserCoupon)
admin.site.register(Transaction)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_at', 'is_active')

    @admin.display(description='Is Active')
    def is_active(self, obj):
        return obj.conditions.validity.is_active

