from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError
from user.models import UserProfile
import json

User = get_user_model()

# Create your models here.
class AllowedUserRule(models.Model):
    user = models.ManyToManyField(
        User,
        verbose_name='users',
        blank=True
    )

    all_users = models.BooleanField(
        default=False, 
        verbose_name='all users'
    )

    def __str__(self):
        return 'Allowed User Rule No.{0}'.format(self.id)

class MaxUsesRule(models.Model):
    max_uses = models.BigIntegerField(
        default=0, 
        verbose_name='max uses'
    )

    is_infinite = models.BooleanField(
        default=False, 
        verbose_name='is infinite'
    )

    uses_per_user = models.IntegerField(
        default=1, 
        verbose_name='uses per user'
    )

    def __str__(self):
        return 'Max Uses Rule No.{0}'.format(self.id)

class ValidityRule(models.Model):
    expiration_date = models.DateTimeField(
        verbose_name='expiration date'
    )

    is_active = models.BooleanField(
        default=False, 
        verbose_name='is active'
    )

    def __str__(self):
        return 'Validity Rule No.{0}'.format(self.id)
    
class CustomRule(models.Model):
    rule_type = models.CharField(
        max_length=20, 
        verbose_name='rule type'
    )

    rule_name = models.CharField(
        max_length=20, 
        verbose_name='rule name'
    )

    params = models.JSONField(
        verbose_name='params'
    )

    def __str__(self):
        return self.rule_name
    
class Discount(models.Model):
    TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('flat', 'Flat'),
    )

    type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        verbose_name='type'
    )

    value = models.IntegerField(
        default=0, 
        verbose_name='value'
    )

    def __str__(self):
        if self.type == 'percentage':
            return '{0}% Discount'.format(self.value)
        else:
            return 'Flat {0} Discount'.format(self.value)

class RuleSet(models.Model):
    allowed_users = models.ForeignKey(
        AllowedUserRule, 
        on_delete=models.CASCADE, 
        verbose_name='allowed user rule'
    )

    max_uses = models.ForeignKey(
        MaxUsesRule, 
        on_delete=models.CASCADE, 
        verbose_name='max uses rule'
    )

    validity = models.ForeignKey(
        ValidityRule, 
        on_delete=models.CASCADE, 
        verbose_name='validity rule'
    )

    custom_rules = models.ManyToManyField(
        CustomRule, 
        verbose_name='custom rules', 
        blank=True
    )

    def __str__(self):
        return 'Rule Set No.{0}'.format(self.id)
        

class Coupon(models.Model):
    code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='code'
    )

    discount = models.ForeignKey(
        Discount, 
        on_delete=models.CASCADE, 
        verbose_name='discount'
    )

    times_used = models.IntegerField(
        default=0, 
        verbose_name='times used'
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='created at', 
        editable=False
    )

    ruleset = models.ForeignKey(
        RuleSet, 
        on_delete=models.CASCADE, 
        verbose_name='rule set'
    )

    def get_discount(self):
        return {
            'type': self.discount.type,
            'value': self.discount.value
        }

    def get_discounted_value(self, initial_value):
        discount = self.get_discount()
        if discount['type'] == 'percentage':
            new_price = initial_value - ((initial_value * discount['value']) / 100)
            new_price = new_price if new_price >= 0.0 else 0.0
        else:
            new_price = initial_value - discount['value']
            new_price = new_price if new_price >= 0.0 else 0.0
        
        return new_price
    

class UserCoupon(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user'
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        verbose_name='coupon'
    )

    times_used = models.IntegerField(
        default=0,
        verbose_name='times used',
        editable=False
    )


class RewardTermsAndConditions(models.Model):
    title = models.CharField(
        max_length=100
    )

    condition_type = models.CharField(
        max_length=20,
        choices=(
            ('signup', 'Signup'),
            ('purchase', 'Purchase'),
            ('referral', 'Referral'),
            ('other', 'Other')
        )
    )

    condition = models.JSONField(
        verbose_name='params',
        help_text='JSON object containing the condition parameters such as "minimun_days":0, "minimum_purchase":100$ etc.'
    )

    is_active = models.BooleanField(
        default=False, 
        verbose_name='is active'
    )

    def __str__(self):
        return json.dumps(self.condition)



class Gems(models.Model):
    name = models.CharField(
        max_length=100
    )

    value = models.IntegerField(
        default=1,
        help_text="The currency value of the gem"
    )

    terms_and_conditions = models.ManyToManyField(
        RewardTermsAndConditions, 
        verbose_name='terms and conditions',
        blank=True
    )

    def __str__(self):
        return self.name
    

class Points(models.Model):
    name = models.CharField(
        max_length=100
    )

    value = models.IntegerField(
        default=1,
        help_text="The currency value of the unit point"
    )

    terms_and_conditions = models.ManyToManyField(
        RewardTermsAndConditions, 
        verbose_name='terms and conditions'
    )

    def __str__(self):
        return self.name
    


class UserRewardWallet(models.Model):
    user = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        verbose_name='user'
    )

    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ['gems', 'points']
        },
        help_text='The type of the reward object'
    )

    object_id = models.PositiveIntegerField(
        help_text='The ID of the reward object'
    )

    reward_object = GenericForeignKey(
        'content_type', 
        'object_id'
    )

    quantity = models.IntegerField(
        default=1, 
        verbose_name='quantity'
    )

    earned_from = models.CharField(
        max_length=100, 
        verbose_name='earned from'
    )

    earned_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='earned at', 
        editable=False
    )

    expires_at = models.DateTimeField(
        verbose_name='expires at'
    )

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.reward_object)

    def is_expired(self):
        return self.expires_at < timezone.now()


class PromoCode(models.Model):
    issuer = models.CharField(
        max_length=100,
        verbose_name='issuer'
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='promo code'
    )

    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        verbose_name='discount'
    )

    conditions = models.ForeignKey(
        RuleSet,
        on_delete=models.CASCADE,
        verbose_name='conditions'
    )

    redemption_count = models.IntegerField(
        default=0,
        verbose_name='redemption count'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='created at',
        editable=False
    )

    description = models.TextField(
        verbose_name='description'
    )

    def __str__(self):
        return self.code
    

    def get_discounted_value(self, initial_value):
        discount = self.discount
        if discount.type == 'percentage':
            new_price = initial_value - ((initial_value * discount.value)/ 100)
            new_price = new_price if new_price >= 0.0 else 0.0
            return new_price
        else:
            new_price = initial_value - discount.value
            new_price = new_price if new_price >= 0.0 else 0.0
            return new_price


class Transaction(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name='user',
        related_name='user_transactions'
    )

    entity_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ['gems', 'points', 'coupon', 'promocode']
        }
    )

    entity_object_id = models.PositiveIntegerField()

    entity = GenericForeignKey('entity_content_type', 'entity_object_id')

    action = models.CharField(
        max_length=20,
        choices=(
            ('credit', 'Credit'),
            ('debit', 'Debit'),
            ('redeem', 'Redeem')
        )
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='timestamp'
    )

    details = models.TextField(
        verbose_name='details',
        null=True,
        blank=True
    )

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.user, self.entity)
