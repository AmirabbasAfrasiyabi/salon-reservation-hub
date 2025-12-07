from django.db import models
from django.utils.text import slugify

# Create your models here.

class Page(models.Model):
    title = models.CharField(verbose_name="title", max_length=100)
    slug = models.SlugField(verbose_name="slug")
    content = models.TextField(null=True, blank=True , verbose_name="content")

    is_active = models.BooleanField(verbose_name="active", default=True)
    show_in_menu = models.BooleanField(verbose_name="show in menu", default=True)

    order = models.IntegerField(verbose_name="order", default=0)

    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

    class Meta:
        verbose_name = 'صفحه'
        verbose_name_plural = 'صفحات'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

class ContactMessage(models.Model):

    STATUS_CHOICES = [
        ('new', 'جدید'),
        ('in_progress', 'در حال بررسی'),
        ('answered', 'پاسخ داده شده'),
        ('closed', 'بسته شده'),
    ]

    full_name = models.CharField(verbose_name="full name", max_length=100)
    email = models.EmailField(verbose_name="email", max_length=100)
    phone_number = models.CharField(verbose_name="phone number", max_length=100)


    #subject
    subject = models.CharField(verbose_name="subject", max_length=100)
    message = models.TextField(verbose_name="message")

    #status
    status = models.CharField(choices=STATUS_CHOICES, max_length=100, verbose_name="status")

    #response
    response = models.CharField(verbose_name="response", max_length=100)
    response_at = models.DateTimeField(verbose_name="response at", auto_now_add=True)

    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class AboutUs(models.Model):
    # محتوای اصلی
    title = models.CharField(max_length=200, verbose_name='عنوان')
    subtitle = models.CharField(max_length=300, null=True, blank=True, verbose_name='زیرعنوان')

    main_content = models.TextField(verbose_name='محتوای اصلی')

    # تصاویر
    main_image = models.ImageField(
        upload_to='about/',
        null=True,
        blank=True,
        verbose_name='تصویر اصلی'
    )

    # آمار سایت
    total_salons = models.PositiveIntegerField(default=0, verbose_name='تعداد آرایشگاه‌ها')
    total_stylists = models.PositiveIntegerField(default=0, verbose_name='تعداد آرایشگران')
    total_customers = models.PositiveIntegerField(default=0, verbose_name='تعداد مشتریان')
    total_reservations = models.PositiveIntegerField(default=0, verbose_name='تعداد رزروها')

    # اطلاعات تماس
    company_name = models.CharField(max_length=200, verbose_name='نام شرکت')
    phone = models.CharField(max_length=11, verbose_name='تلفن')
    email = models.EmailField(verbose_name='ایمیل')
    address = models.TextField(verbose_name='آدرس')

    # شبکه‌های اجتماعی
    instagram = models.URLField(null=True, blank=True, verbose_name='اینستاگرام')
    telegram = models.URLField(null=True, blank=True, verbose_name='تلگرام')
    whatsapp = models.CharField(max_length=11, null=True, blank=True, verbose_name='واتساپ')
    linkedin = models.URLField(null=True, blank=True, verbose_name='لینکدین')

    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'درباره ما'
        verbose_name_plural = 'درباره ما'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # فقط یک رکورد از این مدل مجاز است
        if not self.pk and AboutUs.objects.exists():
            raise ValueError('فقط یک رکورد از صفحه درباره ما مجاز است')
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """
    اعضای تیم
    """
    full_name = models.CharField(max_length=200, verbose_name='نام و نام خانوادگی')
    position = models.CharField(max_length=100, verbose_name='سمت')

    bio = models.TextField(null=True, blank=True, verbose_name='بیوگرافی')

    photo = models.ImageField(upload_to='team/', verbose_name='عکس')

    # شبکه‌های اجتماعی
    email = models.EmailField(null=True, blank=True, verbose_name='ایمیل')
    linkedin = models.URLField(null=True, blank=True, verbose_name='لینکدین')
    instagram = models.URLField(null=True, blank=True, verbose_name='اینستاگرام')

    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class Testimonial(models.Model):
    """
    نظرات مشتریان (برای صفحه اصلی و درباره ما)
    """
    customer_name = models.CharField(max_length=200, verbose_name='نام مشتری')
    customer_position = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='سمت/شغل'
    )

    content = models.TextField(verbose_name='متن نظر')

    rating = models.PositiveIntegerField(
        default=5,
        verbose_name='امتیاز',
        help_text='از 1 تا 5'
    )

    avatar = models.ImageField(
        upload_to='testimonials/',
        null=True,
        blank=True,
        verbose_name='عکس'
    )

    is_featured = models.BooleanField(default=False, verbose_name='نمایش در صفحه اصلی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'نظر مشتری'
        verbose_name_plural = 'نظرات مشتریان'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"نظر {self.customer_name}"


class SiteSettings(models.Model):
    """
    تنظیمات عمومی سایت
    """
    # اطلاعات سایت
    site_name = models.CharField(max_length=200, verbose_name='نام سایت')
    site_tagline = models.CharField(max_length=300, verbose_name='شعار سایت')
    site_description = models.TextField(verbose_name='توضیحات سایت')

    # لوگو و فاویکون
    logo = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='لوگو')
    favicon = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='فاویکون')

    # اطلاعات تماس
    contact_email = models.EmailField(verbose_name='ایمیل تماس')
    contact_phone = models.CharField(max_length=11, verbose_name='تلفن تماس')
    support_phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='تلفن پشتیبانی')

    # شبکه‌های اجتماعی
    instagram = models.URLField(null=True, blank=True, verbose_name='اینستاگرام')
    telegram = models.URLField(null=True, blank=True, verbose_name='تلگرام')
    whatsapp = models.CharField(max_length=11, null=True, blank=True, verbose_name='واتساپ')

    # تنظیمات سئو
    google_analytics_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='کد Google Analytics'
    )

    # تنظیمات عملیاتی
    site_active = models.BooleanField(default=True, verbose_name='سایت فعال')
    maintenance_mode = models.BooleanField(default=False, verbose_name='حالت تعمیر و نگهداری')
    maintenance_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='پیام حالت تعمیر'
    )

    # کمیسیون
    platform_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name='درصد کمیسیون پلتفرم'
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # فقط یک رکورد از این مدل مجاز است
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('فقط یک رکورد از تنظیمات سایت مجاز است')
        super().save(*args, **kwargs)


class Slider(models.Model):
    """
    اسلایدر صفحه اصلی
    """
    title = models.CharField(max_length=200, verbose_name='عنوان')
    subtitle = models.CharField(max_length=300, null=True, blank=True, verbose_name='زیرعنوان')

    image = models.ImageField(upload_to='sliders/', verbose_name='تصویر')

    button_text = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='متن دکمه'
    )
    button_link = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='لینک دکمه'
    )

    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'اسلاید'
        verbose_name_plural = 'اسلایدر'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title