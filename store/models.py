from django.db import models
from django.utils.text import slugify
from django.conf import settings


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


class ImageURLWrapper:
    """Wraps a URL string to mimic Django ImageField .url interface."""
    def __init__(self, url_string):
        self._url = url_string

    @property
    def url(self):
        return self._url or ""

    def __str__(self):
        return self._url or ""

    def __bool__(self):
        return bool(self._url)


class Mood(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    image_url = models.URLField(max_length=1024, blank=True, null=True)

    @property
    def image(self):
        return ImageURLWrapper(self.image_url)

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
    slug = models.SlugField(unique=True, blank=True, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    cover_image_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Primary Cover Image (500x500)")
    image_2_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Product Image 2 (500x500)")
    image_3_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Product Image 3 (500x500)")

    @property
    def cover_image(self):
        return ImageURLWrapper(self.cover_image_url)

    @property
    def all_images(self):
        """Returns up to 3 non-empty image URLs."""
        imgs = []
        if self.cover_image_url:
            imgs.append(self.cover_image_url)
        if self.image_2_url:
            imgs.append(self.image_2_url)
        if self.image_3_url:
            imgs.append(self.image_3_url)
        return imgs

    @property
    def has_multiple_images(self):
        return len(self.all_images) > 1

    # vendor nullable — admin-managed inventory, no vendor portal
    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE, db_index=True)
    moods = models.ManyToManyField(Mood, related_name='books', blank=True)
    vendor = models.ForeignKey('vendors.Vendor', related_name='books',
                               on_delete=models.SET_NULL, null=True, blank=True)

    LANGUAGE_CHOICES = (
        ('OD', 'Odia'),
        ('EN', 'English'),
        ('HI', 'Hindi'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN', db_index=True)

    # Bahi Hata Highlights
    is_trending_in_odisha = models.BooleanField(default=False, db_index=True)
    is_odisha_heritage = models.BooleanField(default=False, db_index=True)
    is_bestseller = models.BooleanField(default=False, db_index=True)
    is_popular = models.BooleanField(default=False, db_index=True)

    stock = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return round(self.price - discount_amount, 2)
        return self.price

    @property
    def discount_price(self):
        return self.final_price if self.discount_percentage > 0 else None

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class BookCombo(models.Model):
    """Admin-curated bundles of 2+ books sold at a special combo price."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    books = models.ManyToManyField(Book, related_name='combos')
    combo_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Final price for the entire combo bundle"
    )
    cover_image_url = models.URLField(
        max_length=1024, blank=True, null=True,
        help_text="Optional banner/cover image for the combo"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def cover_image(self):
        return ImageURLWrapper(self.cover_image_url)

    @property
    def original_total(self):
        """Sum of individual final prices of all books in the combo."""
        return sum(b.final_price for b in self.books.all())

    @property
    def savings(self):
        return round(self.original_total - self.combo_price, 2)

    @property
    def savings_percentage(self):
        orig = self.original_total
        if orig > 0:
            return int((self.savings / orig) * 100)
        return 0

    @property
    def all_in_stock(self):
        return all(b.in_stock for b in self.books.all())

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while BookCombo.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Book Combo"
        verbose_name_plural = "Book Combos"


class Offer(models.Model):
    """
    Site-wide discount offers / coupons managed entirely by admin.
    Supports percentage off, flat amount off, and combo-specific discounts.
    """
    OFFER_TYPE_CHOICES = (
        ('PERCENTAGE', 'Percentage Discount (%)'),
        ('FLAT', 'Flat Amount Off (₹)'),
        ('COMBO_EXTRA', 'Extra % Off on Combos'),
    )

    name = models.CharField(max_length=255, help_text="Internal label e.g. 'Odia Month Sale'")
    code = models.CharField(
        max_length=30, unique=True, blank=True,
        help_text="Coupon code customers enter. Leave blank to auto-generate."
    )
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='PERCENTAGE')
    discount_value = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Percentage (%) or flat ₹ amount depending on type"
    )
    minimum_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Minimum cart value required to apply this offer (0 = no minimum)"
    )
    max_discount_cap = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Max ₹ discount for percentage types. Leave blank = unlimited"
    )

    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Total redemptions allowed. Leave blank = unlimited"
    )
    per_user_limit = models.PositiveIntegerField(
        default=1,
        help_text="Max times a single user can redeem this code"
    )
    times_used = models.PositiveIntegerField(default=0, editable=False)

    applies_to_combos_only = models.BooleanField(
        default=False,
        help_text="Discount applies only to combo items in cart"
    )
    applies_to_category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Restrict discount to a category. Leave blank = store-wide"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Offer / Coupon"
        verbose_name_plural = "Offers & Coupons"

    def save(self, *args, **kwargs):
        if not self.code:
            import random, string
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    @property
    def is_valid_now(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, cart_total):
        """Returns the ₹ discount amount for a given cart total."""
        if not self.is_valid_now:
            return 0
        if cart_total < self.minimum_order_value:
            return 0
        if self.offer_type in ('PERCENTAGE', 'COMBO_EXTRA'):
            raw = (cart_total * self.discount_value) / 100
            if self.max_discount_cap:
                return min(raw, self.max_discount_cap)
            return round(raw, 2)
        elif self.offer_type == 'FLAT':
            return min(self.discount_value, cart_total)
        return 0

    def __str__(self):
        return f"{self.name} [{self.code}]"


class BookReview(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.book.title}"


class MagazineEdition(models.Model):
    """
    Abhilasha Annual Magazine editions.
    Supports stock, pricing, multi-image previews, and order tracking.
    """
    LANGUAGE_CHOICES = (
        ('BI', 'Bilingual (Odia & Hindi)'),
        ('OD', 'Odia (ଓଡ଼ିଆ)'),
        ('HI', 'Hindi (हिन्दी)'),
        ('EN', 'English'),
    )

    title = models.CharField(max_length=255, help_text="e.g. Abhilasha Annual Literary Edition 2026")
    slug = models.SlugField(unique=True, blank=True)
    edition_year = models.CharField(max_length=20, default="2026", help_text="e.g. 2026, 2025-26")
    issue_number = models.CharField(max_length=50, default="Annual Edition", help_text="e.g. Annual Edition, Vol. 14")
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='BI')
    description = models.TextField(help_text="Editorial theme, contents, highlights, and featured authors")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=199.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=50, help_text="Available print copies")

    cover_image_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Primary Cover (500x500)")
    image_2_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Inner Page / TOC Preview (500x500)")
    image_3_url = models.URLField(max_length=1024, blank=True, null=True, help_text="Back Cover / Editorial Preview (500x500)")

    is_current_edition = models.BooleanField(default=False, help_text="Highlight as the current flagship annual edition")
    is_active = models.BooleanField(default=True)
    total_pages = models.PositiveIntegerField(default=128, blank=True, null=True)
    chief_editor = models.CharField(max_length=255, default="Abhilasha Editorial Board", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def cover_image(self):
        return ImageURLWrapper(self.cover_image_url)

    @property
    def all_images(self):
        imgs = []
        if self.cover_image_url:
            imgs.append(self.cover_image_url)
        if self.image_2_url:
            imgs.append(self.image_2_url)
        if self.image_3_url:
            imgs.append(self.image_3_url)
        return imgs

    @property
    def has_multiple_images(self):
        return len(self.all_images) > 1

    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return round(self.price - discount_amount, 2)
        return self.price

    @property
    def discount_price(self):
        return self.final_price if self.discount_percentage > 0 else None

    @property
    def savings(self):
        if self.discount_percentage > 0:
            return round(self.price - self.final_price, 2)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while MagazineEdition.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.is_current_edition:
            # Unmark other current editions
            MagazineEdition.objects.filter(is_current_edition=True).exclude(pk=self.pk).update(is_current_edition=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.edition_year})"

    class Meta:
        ordering = ['-edition_year', '-created_at']
        verbose_name = "Magazine Edition"
        verbose_name_plural = "Magazine Editions"


class MagazineSubmission(models.Model):
    """
    Submissions from writers for Abhilasha Annual Magazine (Hindi / Odia).
    Managed through Admin Panel and forwarded to theabhilasha14@gmail.com.
    """
    LANGUAGE_CHOICES = (
        ('OD', 'Odia (ଓଡ଼ିଆ)'),
        ('HI', 'Hindi (हिन्दी)'),
        ('EN', 'English'),
    )
    GENRE_CHOICES = (
        ('POETRY', 'Poetry / କବିତା / कविता'),
        ('STORY', 'Short Story / ଗଳ୍ପ / लघु कथा'),
        ('ESSAY', 'Essay / ପ୍ରବନ୍ଧ / निबंध'),
        ('ARTICLE', 'Literary & Cultural Article / ସାହିତ୍ୟିକ ଆଲେଖ୍ୟ'),
    )
    STATUS_CHOICES = (
        ('RECEIVED', 'Received / ପ୍ରାପ୍ତ'),
        ('UNDER_REVIEW', 'Under Review / ବିଚାରାଧୀନ'),
        ('SELECTED', 'Selected for Publication / ମନୋନୀତ'),
        ('PUBLISHED', 'Published / ପ୍ରକାଶିତ'),
        ('REJECTED', 'Not Selected'),
    )

    author_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='OD')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='POETRY')
    title_of_work = models.CharField(max_length=255)
    content_text = models.TextField(help_text="The submitted writing text or synopsis")
    author_bio = models.TextField(blank=True, help_text="Short bio and address/district")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    admin_notes = models.TextField(blank=True, help_text="Internal notes by editorial board")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title_of_work} by {self.author_name} ({self.get_language_display()})"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Magazine Submission"
        verbose_name_plural = "Magazine Submissions"
