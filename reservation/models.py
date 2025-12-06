from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import TimeField
from django.utils import timezone
from account.models import User,CustomerProfile,StylistProfile
from salon.models import Salon,Service

class TimeSlot(models.Model):
    stylist = models.ForeignKey(StylistProfile,on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time: TimeField = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)

    is_available = models.BooleanField(default=True , verbose_name='is available')

    class Meta:
        ordering = ['-date']
        verbose_name = 'time slot'
        verbose_name_plural = 'time slots'

    def __str__(self):
        return f'{self.stylist} - {self.date}'

    def is_past(self):
        """بررسی گذشته بودن زمان"""
        from datetime import datetime
        slot_datetime = datetime.combine(self.date, self.start_time)
        return timezone.now() > timezone.make_aware(slot_datetime)

class Reservation(models.Model):

    objects = None
    STATUS_CHOICES = [
        ('pending' , 'pending'),
        ('confirmed' , 'confirmed'),
        ('cancelled' , 'cancelled'),
        ('rejected' , 'rejected'),
        ('completed' , 'completed'),
    ]

    reservation_number = models.CharField(max_length=10, unique=True , verbose_name='reservation number')
    customer = models.ForeignKey(CustomerProfile,on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon,on_delete=models.CASCADE)
    stylist = models.ForeignKey(StylistProfile,on_delete=models.CASCADE)
    service = models.ManyToManyField(Service , related_name='reservation' , blank=True , verbose_name='service')

    #date
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    is_available = models.BooleanField(default=True , verbose_name='is available')

    #price
    total_price = models.DecimalField(max_digits=10, decimal_places=0 , verbose_name='total price' , default=0 , validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10 , decimal_places=0 , verbose_name='discount amount' , default=0 , validators=[MinValueValidator(0)])
    final_price = models.DecimalField(max_digits=10 , decimal_places=0 , verbose_name='final price' , default=0 , validators=[MinValueValidator(0)])

    #status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending' , verbose_name='status')

    #date
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='created at')
    updated_at = models.DateTimeField(auto_now=True , verbose_name='updated at')
    confirmed_at = models.DateTimeField(auto_now=True , verbose_name='confirmed at')
    cancelled_at = models.DateTimeField(auto_now=True , verbose_name='cancelled at')

    class Meta:
        verbose_name = 'reservation'
        verbose_name_plural = 'reservations'
        ordering = ['-date']

    def __str__(self):
        return f'{self.salon} - {self.date}'

    def save(self, *args, **kwargs):
        # تولید شماره رزرو اگر وجود نداشته باشد
        if not self.reservation_number:
            import random
            import string
            while True:
                number = 'RES' + ''.join(random.choices(string.digits, k=10))
                if not Reservation.objects.filter(reservation_number=number).exists():
                    self.reservation_number = number
                    break

        # محاسبه قیمت نهایی
        self.final_price = self.total_price - self.discount_amount

        super().save(*args, **kwargs)

    def can_cancel(self):
        """بررسی امکان لغو رزرو (حداقل 24 ساعت قبل)"""
        from datetime import datetime, timedelta
        reservation_datetime = datetime.combine(self.date, self.start_time)
        now = timezone.now()
        return now < timezone.make_aware(reservation_datetime) - timedelta(hours=24)

    def is_past(self):
        """بررسی گذشته بودن زمان رزرو"""
        from datetime import datetime
        reservation_datetime = datetime.combine(self.date, self.end_time)
        return timezone.now() > timezone.make_aware(reservation_datetime)

class ReservationPolicy(models.Model):

    salon = models.ForeignKey(Salon,on_delete=models.CASCADE)

    free_canceling_hours = models.PositiveSmallIntegerField(default=24 , validators=[MinValueValidator(24)] , verbose_name='free_canceling_hours')

    canceling_free_percentage = models.PositiveSmallIntegerField(default=0 , verbose_name='canceling_free_percentage' , help_text='Percentage of the reservation amount that will be deducted as a penalty')

    policy_text = models.TextField(blank=True , verbose_name='policy_text' , help_text='The text of the reservation policy')

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'reservation policy'
        verbose_name_plural = 'reservation policies'


    def __str__(self):
        return f'{self.salon}'

    def calculate_canceling_fee(self , reservation_price , hour_before ):
        if hour_before > self.free_canceling_hours:
            return 0
        return (reservation_price * self.canceling_free_percentage) / 100


class ReservationReminder(models.Model):

    REMINDER_TYPE_CHOICES = [
        ('sms' , 'sms'),
        ('email' , 'email'),
        ('notify' , 'notify'),
    ]

    reservation = models.ForeignKey(Reservation,on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES, verbose_name='reminder_type')
    hour_before = models.PositiveIntegerField(default=24 , validators=[MinValueValidator(24)] , verbose_name='hour_before')
    schedule_time = models.DateTimeField(default=timezone.now , verbose_name='schedule_time')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now , verbose_name='sent_at')

    class Meta:
        verbose_name = 'reminder'
        verbose_name_plural = 'reminders'


    def __str__(self):
        return f'{self.reservation} - {self.reminder_type}'


