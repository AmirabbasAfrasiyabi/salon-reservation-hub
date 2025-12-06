from django.db import models
from django.core.validators import MinValueValidator , MaxValueValidator
from django.db.models import PositiveIntegerField
from django.utils.text import slugify
from account.models import User


# Create your models here.

class PostCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100 , unique=True , allow_unicode=True , verbose_name="Category Name")

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Parent Category")
    description = models.TextField(blank=True , null=True , verbose_name="Description")

    image = models.ImageField(blank=True , null=True , verbose_name="Image")

    order = models.IntegerField(default=0 , blank=True , null=True , verbose_name="Order")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'post category'
        verbose_name_plural = 'post categories'
        ordering = ['order']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name , allow_unicode=True)
        super().save(*args, **kwargs)

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True, verbose_name='slug')
    logo = models.ImageField( upload_to= 'brand/', blank =True  , null=True , verbose_name="Logo")
    description = models.TextField(blank=True , null=True , verbose_name="Description")
    website = models.URLField(blank=True , null=True , verbose_name="Website")

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True, verbose_name='slug')
    description = models.TextField(blank=True , null=True , verbose_name="Description")

    sku = models.CharField(max_length=100 , blank=True , null=True , verbose_name="SKU")
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name="category")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True, verbose_name="brand")

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock: PositiveIntegerField = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2)

    main_image = models.ImageField( upload_to='product/', blank=True , null=True , verbose_name="Logo")

    #status
    is_active= models.BooleanField(default=True , verbose_name="Is active")
    is_bestseller = models.BooleanField(default=True , verbose_name="Is bestseller")

    #rating
    rating_average = models.DecimalField(max_digits=3, decimal_places=2 , default=0 , verbose_name="Rating average")
    rating_count = models.PositiveIntegerField(default=0 , verbose_name="Rating count")

    #statistics
    view_count = models.PositiveIntegerField(default=0 , verbose_name="View count")
    sales_count = models.PositiveIntegerField(default=0 , verbose_name="Sales count")

    #date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_final_price(self):
        """قیمت نهایی با احتساب تخفیف"""
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    def get_discount_percentage(self):
        """درصد تخفیف"""
        if self.discount_price and self.discount_price < self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def is_in_stock(self):
        """بررسی موجود بودن"""
        return self.stock > 0

    def decrease_stock(self, quantity):
        """کاهش موجودی"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.sales_count += quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        """افزایش موجودی"""
        self.stock += quantity
        self.save()

class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="product")
    image = models.ImageField(upload_to='product/', blank=True , null=True , verbose_name="Logo")
    order = models.PositiveIntegerField(default=0 , blank=True , null=True , verbose_name="Order")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'
        ordering = ['order']

    def __str__(self):
        return self.product.name


class ProductAttribute(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="product")
    attribute = models.CharField(max_length=10, blank=True , null=True , verbose_name="Attribute")
    value = models.CharField(max_length=10, blank=True , null=True , verbose_name="Value")

    class Meta:
        verbose_name = 'product attribute'
        verbose_name_plural = 'product attributes'
        ordering = ['product' , 'attribute']

    def __str__(self):
        return self.attribute


class ProductVariation(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="product")

    name = models.CharField(max_length=100, blank=True , null=True , verbose_name="Name")
    sku = models.CharField(max_length=100, blank=True , null=True , verbose_name="SKU")
    description = models.TextField(blank=True , null=True , verbose_name="Description")

    price = models.DecimalField(max_digits=10, decimal_places=0 , null=True ,blank=True,validators=[MinValueValidator(0)] ,verbose_name="Price")

    stock = models.PositiveIntegerField(default=0 , blank=True , null=True , verbose_name="Stock")

    is_active= models.BooleanField(default=True , verbose_name="Is active")

    class Meta:
        verbose_name = 'product variation'
        verbose_name_plural = 'product variations'
        ordering = ['product']

    def __str__(self):
        return self.name

    def get_price(self):
        """قیمت واریانت یا قیمت محصول اصلی"""
        return self.price if self.price else self.product.get_final_price()


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="product")
    code  = models.CharField(max_length=10, blank=True , null=True , verbose_name="Code")
    discount_type = models.CharField(max_length=10, blank=True , null=True , verbose_name="Discount type")
    value = models.CharField(max_length=10, blank=True , null=True , verbose_name="Value")

    usage_limit = models.PositiveIntegerField(default=0 , verbose_name="Usage limit")
    usage_limit_per_user = models.PositiveIntegerField(default=0 , verbose_name="Usage limit per user")

    valid_from = models.DateTimeField(null=True, blank=True, verbose_name="Valid from")
    valid_to = models.DateTimeField(null=True, blank=True, verbose_name="Valid to")

    applicable_products = models.ManyToManyField(Product, blank=True, verbose_name="Applicable products" , related_name='applicable_products')

    description = models.TextField(blank=True , null=True , verbose_name="Description")
    is_active= models.BooleanField(default=True , verbose_name="Is active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'discount'
        verbose_name_plural = 'discounts'
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.max_discount_amount = None

    def __str__(self):
        return self.code

    def is_valid(self):
        """بررسی اعتبار کد تخفیف"""
        from django.utils import timezone
        now = timezone.now()

        if not self.is_active:
            return False

        if now < self.valid_from or now > self.valid_to:
            return False

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False

        return True

    def calculate_discount(self, amount):
        """محاسبه مبلغ تخفیف"""
        if not self.is_valid():
            return 0

        if self.discount_type == 'percentage':
            discount = (amount * self.value) / 100
        else:
            discount = self.value

        # اعمال حداکثر تخفیف
        if self.max_discount_amount and discount > self.max_discount_amount:
            discount = self.max_discount_amount

        return min(discount, amount)