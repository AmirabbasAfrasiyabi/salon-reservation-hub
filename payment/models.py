from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from account.models import User
from cart.models import Order
from reservation.models import Reservation


class PaymentGateway(models.Model):
    """
    درگاه‌های پرداخت
    """
    GATEWAY_CHOICES = [
        ('zarinpal', 'زرین‌پال'),
        ('idpay', 'آیدی‌پی'),
        ('nextpay', 'نکست‌پی'),
        ('payir', 'پی'),
        ('saman', 'سامان'),
        ('mellat', 'ملت'),
        ('parsian', 'پارسیان'),
    ]

    name = models.CharField(
        max_length=50,
        choices=GATEWAY_CHOICES,
        unique=True,
        verbose_name='نام درگاه'
    )

    display_name = models.CharField(max_length=100, verbose_name='نام نمایشی')

    # تنظیمات
    merchant_id = models.CharField(max_length=200, verbose_name='مرچنت کد')
    api_key = models.CharField(max_length=200, null=True, blank=True, verbose_name='API Key')

    # لوگو
    logo = models.ImageField(
        upload_to='payment_gateways/',
        null=True,
        blank=True,
        verbose_name='لوگو'
    )

    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_default = models.BooleanField(default=False, verbose_name='پیش‌فرض')

    # آمار
    total_transactions = models.PositiveIntegerField(default=0, verbose_name='تعداد تراکنش‌ها')
    successful_transactions = models.PositiveIntegerField(default=0, verbose_name='تراکنش‌های موفق')

    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'درگاه پرداخت'
        verbose_name_plural = 'درگاه‌های پرداخت'
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # اگر این درگاه پیش‌فرض است، بقیه را غیر پیش‌فرض کن
        if self.is_default:
            PaymentGateway.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    پرداخت‌ها
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت داده شده'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('order', 'خرید محصول'),
        ('reservation', 'رزرواسیون'),
    ]

    # شماره پرداخت
    payment_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره پرداخت'
    )

    # کاربر
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='کاربر'
    )

    # نوع پرداخت
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        verbose_name='نوع پرداخت'
    )

    # ارجاع به سفارش یا رزرو
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='سفارش'
    )

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='رزرو'
    )

    # درگاه پرداخت
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments',
        verbose_name='درگاه پرداخت'
    )

    # مبلغ
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ (تومان)'
    )

    # وضعیت
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )

    # اطلاعات درگاه
    authority = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='کد Authority'
    )

    ref_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='کد رهگیری'
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='شناسه تراکنش'
    )

    # اطلاعات کارت
    card_number = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        verbose_name='شماره کارت'
    )

    card_hash = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='هش کارت'
    )

    # توضیحات
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    # پیام خطا (در صورت ناموفق بودن)
    error_message = models.TextField(null=True, blank=True, verbose_name='پیام خطا')
    error_code = models.CharField(max_length=50, null=True, blank=True, verbose_name='کد خطا')

    # IP کاربر
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='آی‌پی')

    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['ref_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"پرداخت {self.payment_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        # تولید شماره پرداخت اگر وجود نداشته باشد
        if not self.payment_number:
            import random
            import string
            while True:
                number = 'PAY' + ''.join(random.choices(string.digits, k=10))
                if not Payment.objects.filter(payment_number=number).exists():
                    self.payment_number = number
                    break

        # ثبت زمان پرداخت موفق
        if self.status == 'success' and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    def mark_as_success(self, ref_id, card_number=None):
        """تغییر وضعیت به موفق"""
        self.status = 'success'
        self.ref_id = ref_id
        self.card_number = card_number
        self.paid_at = timezone.now()
        self.save()

        # بروزرسانی وضعیت سفارش یا رزرو
        if self.order:
            self.order.status = 'paid'
            self.order.paid_at = timezone.now()
            self.order.save()

        if self.reservation:
            self.reservation.status = 'confirmed'
            self.reservation.confirmed_at = timezone.now()
            self.reservation.save()

    def mark_as_failed(self, error_message=None, error_code=None):
        """تغییر وضعیت به ناموفق"""
        self.status = 'failed'
        self.error_message = error_message
        self.error_code = error_code
        self.save()


class Refund(models.Model):
    """
    بازگشت وجه
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('processing', 'در حال پردازش'),
        ('completed', 'انجام شده'),
    ]

    REASON_CHOICES = [
        ('customer_request', 'درخواست مشتری'),
        ('order_cancelled', 'لغو سفارش'),
        ('duplicate_payment', 'پرداخت تکراری'),
        ('technical_issue', 'مشکل فنی'),
        ('other', 'سایر'),
    ]

    # شماره بازگشت وجه
    refund_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره بازگشت'
    )

    # پرداخت اصلی
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='پرداخت'
    )

    # مبلغ بازگشت
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ بازگشت (تومان)'
    )

    # دلیل
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        verbose_name='دلیل بازگشت'
    )

    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    # وضعیت
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )

    # مسئول پردازش
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds',
        verbose_name='پردازش شده توسط'
    )

    # کد رهگیری بازگشت
    refund_ref_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='کد رهگیری بازگشت'
    )

    # یادداشت مدیر
    admin_note = models.TextField(null=True, blank=True, verbose_name='یادداشت مدیر')

    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درخواست')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تایید')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انجام')

    class Meta:
        verbose_name = 'بازگشت وجه'
        verbose_name_plural = 'بازگشت وجوه'
        ordering = ['-created_at']

    def __str__(self):
        return f"بازگشت {self.refund_number} - {self.amount:,} تومان"

    def save(self, *args, **kwargs):
        # تولید شماره بازگشت وجه
        if not self.refund_number:
            import random
            import string
            while True:
                number = 'REF' + ''.join(random.choices(string.digits, k=10))
                if not Refund.objects.filter(refund_number=number).exists():
                    self.refund_number = number
                    break

        super().save(*args, **kwargs)

    def approve(self, user):
        """تایید بازگشت وجه"""
        self.status = 'approved'
        self.processed_by = user
        self.approved_at = timezone.now()
        self.save()

    def complete(self, ref_id):
        """تکمیل بازگشت وجه"""
        self.status = 'completed'
        self.refund_ref_id = ref_id
        self.completed_at = timezone.now()
        self.save()

        # بروزرسانی وضعیت پرداخت
        self.payment.status = 'refunded'
        self.payment.save()


class Transaction(models.Model):
    """
    لاگ تمام تراکنش‌ها (برای گزارش‌گیری و حسابداری)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'پرداخت'),
        ('refund', 'بازگشت وجه'),
        ('commission', 'کمیسیون'),
        ('settlement', 'تسویه'),
    ]

    # شماره تراکنش
    transaction_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره تراکنش'
    )

    # نوع تراکنش
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='نوع تراکنش'
    )

    # مرتبط با
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='پرداخت'
    )

    refund = models.ForeignKey(
        Refund,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='بازگشت وجه'
    )

    # کاربر
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions',
        verbose_name='کاربر'
    )

    # مبلغ (منفی برای برداشت، مثبت برای واریز)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='مبلغ (تومان)'
    )

    # موجودی قبل و بعد
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='موجودی قبل'
    )

    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='موجودی بعد'
    )

    # توضیحات
    description = models.TextField(verbose_name='توضیحات')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تراکنش')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_number} - {self.amount:,} تومان"

    def save(self, *args, **kwargs):
        # تولید شماره تراکنش
        if not self.transaction_number:
            import random
            import string
            while True:
                number = 'TXN' + ''.join(random.choices(string.digits, k=10))
                if not Transaction.objects.filter(transaction_number=number).exists():
                    self.transaction_number = number
                    break

        super().save(*args, **kwargs)


class Wallet(models.Model):
    """
    کیف پول کاربران (برای آرایشگاه‌ها)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='کاربر'
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='موجودی (تومان)'
    )

    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مجموع درآمد'
    )

    total_withdrawn = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مجموع برداشت'
    )

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف پول‌ها'

    def __str__(self):
        return f"کیف پول {self.user.username} - {self.balance:,} تومان"

    def deposit(self, amount, description):
        """واریز به کیف پول"""
        self.balance += amount
        self.total_earned += amount
        self.save()

        # ثبت تراکنش
        Transaction.objects.create(
            transaction_type='payment',
            user=self.user,
            amount=amount,
            balance_before=self.balance - amount,
            balance_after=self.balance,
            description=description
        )

    def withdraw(self, amount, description):
        """برداشت از کیف پول"""
        if self.balance >= amount:
            self.balance -= amount
            self.total_withdrawn += amount
            self.save()

            # ثبت تراکنش
            Transaction.objects.create(
                transaction_type='settlement',
                user=self.user,
                amount=-amount,
                balance_before=self.balance + amount,
                balance_after=self.balance,
                description=description
            )
            return True
        return False