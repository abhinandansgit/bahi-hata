from django.db import models
from django.utils.text import slugify
from django.conf import settings
from vendors.models import Vendor

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Mood(models.Model):
    name = models.CharField(max_length=50) # e.g., "For Rainy Evenings"
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='moods/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Mood.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    
    # Relationships
    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE)
    moods = models.ManyToManyField(Mood, related_name='books', blank=True)
    vendor = models.ForeignKey(Vendor, related_name='books', on_delete=models.CASCADE, null=True)
    
    LANGUAGE_CHOICES = (
        ('OD', 'Odia'),
        ('EN', 'English'),
        ('HI', 'Hindi'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    
    # Bahi Hata Highlights
    is_trending_in_odisha = models.BooleanField(default=False)
    is_odisha_heritage = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return round(self.price - discount_amount, 2)
        return self.price

    def __str__(self):
        return self.title

class BookReview(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.book.title}"
