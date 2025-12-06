from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from account.models import User , SalonOwnerProfile

# Create your models here.

class Salon (models.Model):
    GENDER_TYPE_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    owner = models.ForeignKey(SalonOwnerProfile, on_delete=models.CASCADE)

    #information
    name = models.CharField(max_length=100 , verbose_name='name' , null=True, blank=True)
    slug = models.SlugField(max_length=100, verbose_name='slug' , null=True, blank=True)

    description = models.TextField(verbose_name='description' , null=True, blank=True)
    gender_type = models.CharField(max_length=20, choices=GENDER_TYPE_CHOICES , default='Male')

    #address and location
    address = models.TextField(verbose_name='address' , null=True, blank=True)
    city = models.TextField( max_length=100, verbose_name='city' , null=True, blank=True)
    province = models.TextField( max_length=100, verbose_name='province' , null=True, blank=True)
    country = models.TextField( max_length=100, verbose_name='country' , null=True, blank=True)
    postal_code = models.TextField( max_length=100, verbose_name='postal code' , null=True, blank=True)

    logo = models.ImageField(upload_to='images/' , verbose_name='logo' , null=True, blank=True)

    # Facilities
    has_parking = models.BooleanField(default=False , verbose_name='has_parking' , null=True, blank=True)
    has_wifi = models.BooleanField(default=False , verbose_name='has_wifi' , null=True, blank=True)
    has_food= models.BooleanField(default=False , verbose_name='has_food' , null=True, blank=True)
    has_kids_area = models.BooleanField(default=False , verbose_name='has_kids_area' , null=True, blank=True)

    #rate
    rating_average = models.DecimalField(max_digits=2, decimal_places=2, default=0, verbose_name='rating_average' , null=True, blank=True)
    rating_count = models.IntegerField(default=0 , verbose_name='rating_count' , null=True, blank=True)

    #staff
    is_active = models.BooleanField(default=True, verbose_name='is_active' , null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='is_verified' , null=True, blank=True)

    #date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at' , null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated_at' , null=True, blank=True)

    class Meta:
        verbose_name = 'Salon'
        verbose_name_plural = 'Salon'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.owner} - {self.slug}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.owner}-{self.slug}')
        super().save(*args, **kwargs)


class SalonImage (models.Model):

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/' , verbose_name='image' , null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at' , null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated_at' , null=True, blank=True)
    title = models.CharField(max_length=100 , verbose_name='title' , null=True, blank=True)
    slug = models.SlugField(max_length=100, verbose_name='slug' , null=True, blank=True)

    class Meta:
        verbose_name = 'SalonImage'
        verbose_name_plural = 'SalonImage'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.salon} - {self.title}'

class ServiceCategory (models.Model):

    name = models.CharField(max_length=100 , verbose_name='name' , null=True, blank=True)
    slug = models.SlugField(max_length=100, verbose_name='slug' , null=True, blank=True)
    icon = models.ImageField(upload_to='images/' , verbose_name='icon' , null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='is_active' , null=True, blank=True)

    class Meta:
        verbose_name = 'ServiceCategory'
        verbose_name_plural = 'ServiceCategory'

    def __str__(self):
        return f'{self.name} - {self.slug}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.name}')
        super().save(*args, **kwargs)

class Service(models.Model):

    GENDER_TYPE_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    salon = models.ForeignKey(Salon,on_delete=models.CASCADE,related_name='services', verbose_name='salon' , null=True, blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name='category' , null=True, blank=True)
    name = models.CharField(max_length=100 , verbose_name='name' , null=True, blank=True)
    description = models.TextField(verbose_name='description' , null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='price' , validators=[MinValueValidator(0)],null=True, blank=True)

    discount_price = models.DecimalField(max_digits=10 , decimal_places=0, verbose_name='discount_price' , validators=[MinValueValidator(0)],null=True, blank=True)

    duration = models.PositiveIntegerField(verbose_name='duration' , null=True, blank=True , help_text='Service duration in minutes')

    gender = models.CharField(max_length=20, choices=GENDER_TYPE_CHOICES , default='Male')

    image = models.ImageField(upload_to='images/' , verbose_name='image' , null=True, blank=True)

    is_active = models.BooleanField(default=True, verbose_name='is_active' , null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='is_verified' , null=True, blank=True)
    is_popular = models.BooleanField(default=False, verbose_name='is_popular' , null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at' , null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated_at' , null=True, blank=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Service'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.salon} - {self.name}'

    def get_final_price(self):
        if self.discount_price and self.discount_price <= self.price:
            return self.discount_price
        return self.price

    def get_discount_percentage(self):
        if self.discount_price and self.discount_price <= self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0


class WorkingHours(models.Model):
    """Time for working hours"""
    WEEKDAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE , related_name='working_hours' , verbose_name='salon' , null=True, blank=True)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES , verbose_name='weekday' , null=True, blank=True)
    opening_time = models.TimeField(verbose_name='opening_time' , null=True, blank=True)
    closing_time = models.TimeField(verbose_name='closing_time' , null=True, blank=True)

    is_closed = models.BooleanField(default=False, verbose_name='is_closed' , null=True, blank=True)

    class Meta:
        verbose_name = 'Working Hours'
        verbose_name_plural = 'Working Hours'

    def __str__(self):
        day_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        if self.is_closed:
            return f'{self.salon} - {self.weekday}'
        return f'{self.salon} - {self.weekday} {day_name}'


class StylistSchedule(models.Model):

    WEEKDAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    stylist = models.ForeignKey('account.StylistProfile', on_delete=models.CASCADE, verbose_name='stylist' , null=True, blank=True)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES , verbose_name='weekday' , null=True, blank=True)

    start_time = models.TimeField(verbose_name='start_time' , null=True, blank=True)
    end_time = models.TimeField(verbose_name='end_time' , null=True, blank=True)

    class Meta:
        verbose_name = 'Stylist Schedule'
        verbose_name_plural = 'Stylist Schedule'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.stylist} - {self.weekday}'


class SalonSpecialDay(models.Model):

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE , related_name='special_days' , verbose_name='salon' , null=True, blank=True)
    date = models.DateField(verbose_name='date' , null=True, blank=True)
    is_closed = models.BooleanField(default=False, verbose_name='is_closed' , null=True, blank=True)

    opening_time = models.TimeField(verbose_name='opening_time' , null=True, blank=True)
    closing_time = models.TimeField(verbose_name='closing_time' , null=True, blank=True)

    reason = models.TextField(verbose_name='reason' , null=True, blank=True)

    class Meta:
        verbose_name = 'Salon Special Day'
        verbose_name_plural = 'Salon Special Day'
        ordering = ['-date']

    def __str__(self):
        return f'{self.salon} - {self.date}'
