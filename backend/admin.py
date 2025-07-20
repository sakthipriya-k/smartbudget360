from django.contrib import admin
from .models import UserProfile, Income, Expense

# Register models only once
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'monthly_income', 'monthly_expense', 'monthly_expense_limit')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'date')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date')
