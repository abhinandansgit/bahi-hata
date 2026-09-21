from django.db import models
from django.conf import settings
from store.models import Book, BookCombo, Offer, MagazineEdition


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def book_items_total(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def combo_items_total(self):
        return sum(item.total_price for item in self.combo_items.all())

    @property
    def magazine_items_total(self):
        return sum(item.total_price for item in self.magazine_items.all())

    @property
    def total_price(self):
        return round(self.book_items_total + self.combo_items_total + self.magazine_items_total, 2)

    @property
    def item_count(self):
        book_qty = sum(i.quantity for i in self.items.all())
        combo_qty = sum(i.quantity for i in self.combo_items.all())
        mag_qty = sum(i.quantity for i in self.magazine_items.all())
        return book_qty + combo_qty + mag_qty


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.book.title}"

    @property
    def total_price(self):
        return round(self.book.final_price * self.quantity, 2)

    class Meta:
        unique_together = ('cart', 'book')


class ComboCartItem(models.Model):
    """A BookCombo added to a user's cart."""
    cart = models.ForeignKey(Cart, related_name='combo_items', on_delete=models.CASCADE)
    combo = models.ForeignKey(BookCombo, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × Combo: {self.combo.name}"

    @property
    def total_price(self):
        return round(self.combo.combo_price * self.quantity, 2)

    class Meta:
        unique_together = ('cart', 'combo')


class MagazineCartItem(models.Model):
    """An Abhilasha Magazine edition added to a user's cart."""
    cart = models.ForeignKey(Cart, related_name='magazine_items', on_delete=models.CASCADE)
    edition = models.ForeignKey(MagazineEdition, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × Magazine: {self.edition.title}"

    @property
    def total_price(self):
        return round(self.edition.final_price * self.quantity, 2)

    class Meta:
        unique_together = ('cart', 'edition')


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField()

    # WhatsApp-based checkout — only method
    payment_method = models.CharField(max_length=20, default='WHATSAPP')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    # Coupon / Offer applied
    coupon = models.ForeignKey(Offer, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='orders')
    coupon_code_used = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """A single Book line-item in an order."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # locked price at order time
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.book.title} (Order #{self.order.id})"

    @property
    def total_price(self):
        return round(self.price * self.quantity, 2)


class ComboOrderItem(models.Model):
    """A BookCombo line-item in an order."""
    order = models.ForeignKey(Order, related_name='combo_items', on_delete=models.CASCADE)
    combo = models.ForeignKey(BookCombo, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # locked combo price at order time
    quantity = models.PositiveIntegerField(default=1)
    combo_name_snapshot = models.CharField(max_length=255, blank=True)  # store name at order time

    def save(self, *args, **kwargs):
        if not self.combo_name_snapshot and self.combo_id:
            self.combo_name_snapshot = self.combo.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × Combo: {self.combo_name_snapshot} (Order #{self.order.id})"

    @property
    def total_price(self):
        return round(self.price * self.quantity, 2)


class MagazineOrderItem(models.Model):
    """An Abhilasha Magazine line-item in an order."""
    order = models.ForeignKey(Order, related_name='magazine_items', on_delete=models.CASCADE)
    edition = models.ForeignKey(MagazineEdition, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    title_snapshot = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.title_snapshot and self.edition_id:
            self.title_snapshot = self.edition.title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × Magazine: {self.title_snapshot} (Order #{self.order.id})"

    @property
    def total_price(self):
        return round(self.price * self.quantity, 2)

