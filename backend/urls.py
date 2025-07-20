from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # Expense handling
    path('add-expense/manual/', views.add_expense_view, name='add_expense'),
    path('add-expense/', views.add_expense_page_view, name='add_expense_page'),
    path('upload-bill/', views.upload_bill_view, name='upload_bill'),
    path('expenses/', views.expense_list_view, name='expense_list'),  # ✅ Add this line
]
