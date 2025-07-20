from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_expense = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_expense_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.username

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} Income"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} Expense"
