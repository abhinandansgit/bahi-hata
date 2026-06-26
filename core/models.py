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
