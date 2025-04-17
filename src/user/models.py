from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def _create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_superuser(email, password, **extra_fields)
    

class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(
        unique=True,
        verbose_name=_("Email Address"),
        max_length=255,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name='profile'
    )

    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
        blank=True,
        null=True
    )

    email = models.EmailField(
        verbose_name=_("Email Address"),
        blank=True,
        null=True
    )

    address = models.TextField(
        verbose_name=_("Address"),
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures',
        verbose_name=_("Profile Picture"),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email
