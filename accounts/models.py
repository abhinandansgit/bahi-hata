from django.contrib.auth.models import AbstractUser
from django.db import models

class ImageURLWrapper:
    def __init__(self, url_string):
        self._url = url_string

    @property
    def url(self):
        return self._url or ""

    def __str__(self):
        return self._url or ""

    def __bool__(self):
        return bool(self._url)

class User(AbstractUser):
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture_url = models.URLField(max_length=1024, blank=True, null=True)

    @property
    def profile_picture(self):
        return ImageURLWrapper(self.profile_picture_url)

    def __str__(self):
        return self.username


class Wishlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='wishlists')
    book = models.ForeignKey('store.Book', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} → {self.book.title}"

