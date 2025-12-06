from django.db import models
from django.core.validators import MinValueValidator , MaxValueValidator
from account.models import User , CustomerProfile
from shop.models import Product , ProductVariation , Discount

# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        ordering = ['-created_at']
        verbose_name = 'Cart'
        verbose_name_plural = 'Cart'

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.items = None

    def __str__(self):
        return self.product.name

    def get_total_items(self):
        """تعداد کل آیتم‌ها"""
        return sum(item.quantity for item in self.items.all())

    def get_subtotal(self):
        """مجموع قیمت بدون تخفیف"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total(self):
        """مجموع نهایی"""
        return self.get_subtotal()

    def clear(self):
        """خالی کردن سبد خرید"""
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariation, on_delete=models.CASCADE , null=True , blank=True , related_name='cart_product' , verbose_name='product')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CartItem'
        verbose_name_plural = 'CartItem'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """قیمت کل این آیتم"""
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        # ذخیره قیمت فعلی محصول
        if not self.price:
            if self.variant:
                self.price = self.variant.get_price()
            else:
                self.price = self.product.get_final_price()
        super().save(*args, **kwargs)

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
        ('returned', 'مرجوع شده'),
    ]

    order_number = models.CharField(max_length=10, unique=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=0 , validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=0 , validators=[MinValueValidator(0)])
    shopping_cost = models.DecimalField(max_digits=10, decimal_places=0 , validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=0 , default=0,validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=0 , default=0)

    #address
    shopping_full_name = models.CharField(max_length=120)
    shopping_phone = models.CharField(max_length=120 , verbose_name="Phone number")
    shopping_address = models.CharField(max_length=120 , verbose_name="Address")
    shopping_city = models.CharField(max_length=120 , verbose_name="City")
    shopping_state = models.CharField(max_length=120 , verbose_name="State")
    shopping_zip = models.CharField(max_length=120 , verbose_name="Zip")

    #send information
    tracking_code = models.CharField(max_length=120 , null=True , blank=True,verbose_name="Tracking code")
    shopping_method = models.CharField(max_length=120 , null=True , blank=True,verbose_name="Shopping method")

    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ ارسال')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تحویل')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.order_number} - {self.customer.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # تولید شماره سفارش اگر وجود نداشته باشد
        if not self.order_number:
            import random
            import string
            while True:
                number = 'ORD' + ''.join(random.choices(string.digits, k=10))
                if not Order.objects.filter(order_number=number).exists():
                    self.order_number = number
                    break

        # محاسبه مبلغ نهایی
        self.total = self.subtotal - self.discount_amount + self.shipping_cost + self.tax_amount

        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    variant = models.ForeignKey(ProductVariation , on_delete=models.CASCADE , null=True , blank=True , related_name='order_item' , verbose_name='product')

    product_name = models.CharField(max_length=120)
    product_sku = models.CharField(max_length=120)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2 ,validators=[MinValueValidator(0)] , verbose_name='total price')

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # محاسبه قیمت کل
        self.total_price = self.price * self.quantity

        # ذخیره اطلاعات محصول
        if self.product and not self.product_name:
            self.product_name = self.product.name
            self.product_sku = self.product.sku

        super().save(*args, **kwargs)

class ShoppingMethod(models.Model):
    name = models.CharField(max_length=120 , verbose_name="shopping method name")
    shopping_method = models.CharField(max_length=120)
    description = models.CharField(max_length=120 , verbose_name="shopping method description")

    cost = models.DecimalField(max_digits=10, decimal_places=2 , validators=[MinValueValidator(0)] , verbose_name='cost')

    estimated_days_min = models.PositiveIntegerField(default=0 , verbose_name='Minimum delivery time (days)')
    estimated_days_max = models.PositiveIntegerField(default=0 , verbose_name='Maximum delivery time (days)')

    is_active = models.BooleanField(default=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ShoppingMethod'
        verbose_name_plural = 'ShoppingMethods'

    def __str__(self):
        return self.name



class Address(models.Model):
    """
    آدرس‌های ذخیره شده مشتریان
    """
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='مشتری'
    )

    full_name = models.CharField(max_length=200, verbose_name='نام گیرنده')
    phone = models.CharField(max_length=11, verbose_name='تلفن')

    address = models.TextField(verbose_name='آدرس کامل')
    city = models.CharField(max_length=100, verbose_name='شهر')
    province = models.CharField(max_length=100, verbose_name='استان')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')

    is_default = models.BooleanField(default=False, verbose_name='آدرس پیش‌فرض')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    def save(self, *args, **kwargs):
        # اگر این آدرس پیش‌فرض است، بقیه آدرس‌ها را غیر پیش‌فرض کن
        if self.is_default:
            Address.objects.filter(customer=self.customer, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)