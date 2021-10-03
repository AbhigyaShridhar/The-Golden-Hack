from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    credits = models.IntegerField(default=10000)
    transactions = models.ManyToManyField('Transaction', related_name="stocks_bought_or_sold", blank=False)
    friends = models.ManyToManyField('User', blank=True)
    profit = models.IntegerField(default=0)

#To be extracted by the API

# API

class Stock(models.Model):
    name = models.CharField(max_length=100, default="stock", blank=False, null=False)
    description = models.CharField(max_length=200, default="stocks", blank=False, null=False)


DEFAULT_USER_ID = 1
class Transaction(models.Model):
    stock = models.OneToOneField(Stock, verbose_name="STOCK_ID", primary_key=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=DEFAULT_USER_ID, null=False, blank=False, related_name="Operation_Performed_By", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=False, blank=False)
    #API
    totalExpenditure = models.IntegerField(default=0, blank=False, null=False)

class TransactionHistory(models.Model):
    user = models.OneToOneField(User, default=DEFAULT_USER_ID, primary_key=True, null=False, blank=False, related_name="Transaction_By", on_delete=models.CASCADE)
    intialQuantity = models.IntegerField(default=0, null=False, blank=False)
    finalQuantity = models.IntegerField(default=0, null=False, blank=False)
    stockQuote = models.CharField(max_length=100, default="stock", blank=False, null=False)
    priceAtWhichBought = models.IntegerField(default=0, null=False, blank=False)
    priceAtWhichSold = models.IntegerField(default=0, null=False, blank=False)
    intialCredits = models.IntegerField(default=0, null=False, blank=False)
    finalCredits = models.IntegerField(default=0, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Transaction History"
        db_table = "Transaction_History"
