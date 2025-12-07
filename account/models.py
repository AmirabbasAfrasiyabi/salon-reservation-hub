from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):

    """
    مدل کاربر سفارشی - پایه برای همه انواع کاربران
    """
    USER_TYPE_CHOICES = [
        ('customer', 'customer'),
        ('stylist' , 'stylist'),
        ('salon_owner' , 'salon_owner'),
        ('admin' , 'admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES , default='customer')
    phone_regex = RegexValidator(regex=r'^09\d{9}$', message='Mobile number must be in the format 09xxxxxxxxxx')
    mobile = models.CharField(validators=[phone_regex], max_length=11 , unique=True , blank=True , verbose_name='phone number')
    email = models.EmailField(unique=True,verbose_name='email address')
    is_phone_verified = models.BooleanField(default=False,verbose_name='verified phone number')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='created at')
    updated_at = models.DateTimeField(auto_now=True , verbose_name='updated at')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f"{self.get_full_name() or self.username}"


class CustomerProfile(models.Model):

    GENDER_CHOICES = [
        ('male' , 'male'),
        ('female' , 'female'),
        ('other' , 'other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE , verbose_name='user' , primary_key=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , default='other')
    birth_date = models.DateField(verbose_name='birth date' , null=True, blank=True)
    address = models.TextField(verbose_name='address' , null=True, blank=True)
    city = models.CharField(max_length=20, verbose_name='city' , null=True, blank=True)
    postal_code = models.CharField(max_length=10, verbose_name='postal code' , null=True, blank=True)
    phone = models.CharField(max_length=11 , verbose_name='phone number' , null=True, blank=True)
    email = models.EmailField(verbose_name='email address' , null=True, blank=True)

    """notification"""
    phone_notification = models.BooleanField(default=False , verbose_name='phone notification')
    email_notification = models.BooleanField(default=False , verbose_name='email notification')

    class Meta:
        verbose_name = 'customer profile'
        verbose_name_plural = 'customer profiles'

    def __str__(self):
        return f"profile{self.user.get_full_name()}"

class StylistProfile(models.Model):
    GENDER_CHOICES = [
        ('male' , 'male'),
        ('female' , 'female'),
        ('other' , 'other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE , verbose_name='user' , related_name='stylist_profile')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , default='other' , verbose_name='gender')

    #resume
    experience_years = models.PositiveIntegerField(verbose_name='experience years' , null=True, blank=True , default=0)
    bio = models.TextField(verbose_name='bio', null=True, blank=True , help_text='Descriptions about hairdressers and specialties')
    # specialties = models.ManyToManyField('salon.Service' , verbose_name='specialties',related_name='specialist_stylists' , blank=True)
    certificates = models.FileField(upload_to='certificates' , verbose_name='certificates' , null=True, blank=True , help_text='List of certificates and documents')
    resume = models.FileField(upload_to='resume' , verbose_name='resume' , null=True, blank=True , help_text='Resume document')

    #activitation
    is_active = models.BooleanField(default=False , verbose_name='active')
    is_verified = models.BooleanField(default=False , verbose_name='verified')

    #rate and comment
    rating_average = models.DecimalField(max_digits=3 , decimal_places=2 , default=0,verbose_name='rating average' , null=True, blank=True)
    rating_count = models.PositiveIntegerField(verbose_name='rating count' , null=True, blank=True , default=0)

    class Meta:
        verbose_name = 'stylist profile'
        verbose_name_plural = 'stylist profiles'

    def __str__(self):
        return f"profile{self.user.get_full_name()} _ stylist"

class SalonOwnerProfile(models.Model):
    GENDER_CHOICES = [
        ('male' , 'male'),
        ('female' , 'female'),
        ('other' , 'other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE , verbose_name='user' , related_name='salon_owner_profile')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , default='other')

    business_phone = models.CharField(max_length=11 , verbose_name='phone number' , null=True, blank=True)
    business_email = models.EmailField(verbose_name='email address' , null=True, blank=True)

    # Legal information
    national_id = models.CharField(max_length=11 , verbose_name='national id' , null=True, blank=True)
    business_license = models.CharField(max_length=50 , verbose_name='license code' , null=True, blank=True)
    is_card_image = models.ImageField(upload_to='documents/id_cards' , verbose_name='id_card' , null=True, blank=True)
    license_image = models.ImageField(upload_to='documents/licenses' , verbose_name='licenses image' , null=True, blank=True)

    #activitation
    is_verified = models.BooleanField(default=False , verbose_name='verified')
    verified_at = models.DateTimeField(auto_now_add=True , verbose_name='verified at' , null=True, blank=True)

    # Financial Information
    bank_account = models.CharField(max_length=16 , verbose_name='bank account' , null=True, blank=True)
    shaba_number = models.CharField(max_length=24 , verbose_name='shaba number' , null=True, blank=True)

    class Meta:
        verbose_name = 'owner profile'
        verbose_name_plural = 'owner profiles'

    def __str__(self):
        return f"profile{self.user.get_full_name()} _ account"

class OTPCode(models.Model):

    DoesNotExist = None
    objects = None
    phone_number = models.CharField(max_length=11 , verbose_name='phone number' , null=True, blank=True)
    code = models.CharField(max_length=6, verbose_name='code' , null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='created at' , null=True, blank=True)

    class Meta:
        verbose_name = 'otp code'
        verbose_name_plural = 'otp codes'

    def __str__(self):
        return f"code {self.code}"

    def is_expired(self):
        """بررسی انقضای کد (2 دقیقه)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=2)
