from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from core.enums import UserType, Gender

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email).strip()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', UserType.ADMIN)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(_('email address'), unique=True, blank=False)
    user_type = models.CharField(max_length=15, choices=UserType.choices, default=UserType.CLIENT)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict)
    language_preference = models.CharField(max_length=10, default='tr')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.email

    def is_dietitian(self):
        return self.user_type == UserType.DIETITIAN

    def is_client(self):
        return self.user_type == UserType.CLIENT

    def is_admin(self):
        return self.user_type == UserType.ADMIN
    
class Specialization(BaseModel):
    code = models.SlugField(max_length=50, unique=True, help_text=_("Unique identifier for the specialization"))
    name = models.CharField(max_length=100, help_text=_("Display name of the specialization"))
    description = models.TextField(blank=True, help_text=_("Optional description for further details"))

    class Meta:
        verbose_name = _("Specialization")
        verbose_name_plural = _("Specializations")
        ordering = ['name']

    def __str__(self):
        return self.name

class DietitianProfile(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dietitian_profile'
    )
    specializations = models.ManyToManyField(
        Specialization,
        related_name='dietitians'
    )
    bio = models.TextField(blank=True)
    education = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    certificate_info = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    availability = models.JSONField(default=dict)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True, null=True)
    
    class Meta:
        verbose_name = _('Dietitian Profile')
        verbose_name_plural = _('Dietitian Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"