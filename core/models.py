from django.db import models

class SiteStat(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50) # Can hold "50K", "1,200", "4.9", etc.
    numeric_value = models.FloatField(help_text="Numeric part for 'start from zero' animation", default=0)
    suffix = models.CharField(max_length=20, blank=True, help_text="e.g. '+', '★', ' hrs'")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}"


class ReaderStory(models.Model):
    """
    Public customer reviews and stories for Bahi Hata.
    Displayed on the homepage Reader Stories page-curl carousel.
    """
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, default="Bhubaneswar, Odisha")
    rating = models.PositiveIntegerField(default=5)
    review_text = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def initial(self):
        return self.name[0].upper() if self.name else 'R'

    @property
    def stars(self):
        return '★' * min(max(self.rating, 1), 5)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reader Story"
        verbose_name_plural = "Reader Stories"

    def __str__(self):
        return f"{self.name} ({self.location}) - {self.rating}★"

