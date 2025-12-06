from django.db import models
from django.utils.text import slugify
from account.models import User

# Create your models here.

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True , allow_unicode=True , verbose_name="slug")

    description = models.TextField(null=True, blank=True)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True , verbose_name="parent")

    image = models.ImageField(upload_to='blog/categories',null=True, blank=True , verbose_name="image")

    order = models.PositiveIntegerField(default=0 , verbose_name="order")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی مقاله'
        verbose_name_plural = 'دسته‌بندی مقالات'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'draft'),
        ('published', 'published'),
        ('archived', 'archived'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE , related_name='posts' , verbose_name="author")
    title = models.CharField(max_length=100 , verbose_name="title")
    slug = models.SlugField(max_length=100, unique=True , allow_unicode=True , verbose_name="slug")
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True , verbose_name="content")
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE , related_name='posts' , verbose_name="category")
    status = models.CharField(choices=STATUS_CHOICES, max_length=100, verbose_name="status")

    image_alt = models.ImageField(upload_to='blog/posts' , null=True, blank=True , verbose_name="image")

    is_featured = models.BooleanField(default=False , verbose_name="is_featured")
    allow_comments = models.BooleanField(default=False , verbose_name="allow_comments")

    #statistics
    view_count = models.PositiveIntegerField(default=0 , verbose_name="view_count")
    like_count = models.PositiveIntegerField(default=0 , verbose_name="like_count")
    dislike_count = models.PositiveIntegerField(default=0 , verbose_name="dislike_count")

    rating_time = models.PositiveIntegerField(default=0 , verbose_name="rating_time")

    #date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انتشار')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at', '-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.reading_time = None

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # ایجاد اسلاگ
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        # محاسبه زمان مطالعه (فرض: 200 کلمه در دقیقه)
        if not self.reading_time:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)

        # ثبت تاریخ انتشار
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def increase_view(self):
        """افزایش تعداد بازدید"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE , related_name='comments' , verbose_name="post")
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='comments' , verbose_name="user")
    content = models.TextField(null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=100, verbose_name="status")
    like_count = models.PositiveIntegerField(default=0 , verbose_name="like_count")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.replies = None

    def __str__(self):
        return f"نظر {self.user.username} در {self.post.title}"

    def get_replies(self):
        """دریافت پاسخ‌های این نظر"""
        return self.replies.filter(status='approved')


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE , related_name='likes' , verbose_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='likes' , verbose_name="user")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')

    class Meta:
        verbose_name = 'لایک نظر'
        verbose_name_plural = 'لایک‌های نظرات'
        unique_together = ['comment', 'user']

    def __str__(self):
        return f"{self.user.username} - نظر {self.comment.id}"


class Newsletter(models.Model):
    """
    خبرنامه - لیست ایمیل‌های مشترکین
    """
    email = models.EmailField(unique=True, verbose_name='ایمیل')

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت')
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ لغو عضویت')

    class Meta:
        verbose_name = 'خبرنامه'
        verbose_name_plural = 'خبرنامه'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def unsubscribe(self):
        """لغو عضویت"""
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
