from django.db import models
from django.utils import timezone

# Create your models here.
class Transaction(models.Model):
    date_of_narration= models.DateField(default=timezone.now)
    narration=models.CharField(max_length=500)
    refno=models.CharField(max_length=256)
    date_of_transaction = models.DateField(default=timezone.now)
    widthdrawl=  models.DecimalField(max_digits=10, decimal_places=2)
    deposit=  models.DecimalField(max_digits=10, decimal_places=2)
    balance=  models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.narration
