from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.core.files.storage import FileSystemStorage
from .models import UserProfile, Expense
import pytesseract
from PIL import Image
import re
import os

# ✅ Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# ✅ Signup View
def signup_view(request):
    if request.method == 'POST':
        first = request.POST['first_name']
        last = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        gender = request.POST['gender']
        income = request.POST['income']
        expense = request.POST['expense']
        limit = request.POST['limit']

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first,
            last_name=last
        )

        UserProfile.objects.create(
            user=user,
            gender=gender,
            monthly_income=income,
            monthly_expense=expense,
            monthly_expense_limit=limit
        )

        login(request, user)
        return redirect('dashboard')

    return render(request, 'signup.html')


# ✅ Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


# ✅ Dashboard View
@login_required(login_url='/login/')
def dashboard_view(request):
    profile = request.user.userprofile
    total_spent = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    remaining_expense = float(profile.monthly_expense_limit) - float(total_spent)

    warning = ""
    if total_spent > float(profile.monthly_expense_limit):
        warning = "⚠️ You have exceeded your expense limit!"

    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    context = {
        'income': float(profile.monthly_income),
        'expense': remaining_expense,
        'limit': float(profile.monthly_expense_limit),
        'original_expense': float(profile.monthly_expense),
        'income_list': [float(profile.monthly_income)],
        'expense_list': [float(total_spent)],
        'labels': ['This Month'],
        'warning': warning,
        'expenses': expenses,
        'total_spent': total_spent
    }
    return render(request, 'dashboard.html', context)


# ✅ Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


# ✅ Add Expense View
@login_required(login_url='/login/')
def add_expense_view(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        category = request.POST['category']
        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            date=timezone.now().date()
        )
        return redirect('dashboard')
    return render(request, 'add_expense.html')


# ✅ View All Expenses
@login_required(login_url='/login/')
def expense_list_view(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expense_list.html', {'expenses': expenses})


# ✅ Upload Bill View (OCR + Category + Save)
@login_required(login_url='/login/')
def upload_bill_view(request):
    if request.method == 'POST' and request.FILES.get('bill_image'):
        bill_image = request.FILES['bill_image']
        fs = FileSystemStorage()
        filename = fs.save(bill_image.name, bill_image)
        file_path = fs.path(filename)

        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        os.remove(file_path)

        # 👉 Smart total extraction
        total = 0
        lines = text.splitlines()
        for line in lines:
            if 'total' in line.lower():
                match = re.search(r'([\d,.]+)', line)
                if match:
                    total = match.group(1).replace(',', '')
                    try:
                        total = float(total)
                    except:
                        total = 0
                    break

        # Fallback if total not found
        if total == 0:
            matches = re.findall(r'([\d,]+\.\d{2})', text)
            if matches:
                total = max(float(m.replace(',', '')) for m in matches)

        # 👉 Category Detection
        text_lower = text.lower()
        if any(word in text_lower for word in ['restaurant', 'menu', 'food', 'daal', 'chapati', 'curd', 'rice']):
            category = 'Restaurant'
        elif any(word in text_lower for word in ['tshirt', 'pants', 'bill', 'shopping']):
            category = 'Shopping'
        elif any(word in text_lower for word in ['electricity', 'current', 'eb']):
            category = 'Electricity'
        else:
            category = 'General'

        if total:
            Expense.objects.create(
                user=request.user,
                amount=total,
                category=category,
                date=timezone.now().date()
            )
            return redirect('dashboard')
        else:
            return render(request, 'upload_bill.html', {'error': 'Could not extract total amount from image'})

    return render(request, 'upload_bill.html')


# ✅ Settings View
@login_required(login_url='/login/')
def settings_view(request):
    return render(request, 'settings.html')


# ✅ Edit Profile View
@login_required(login_url='/login/')
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        request.user.email = request.POST['email']
        profile.gender = request.POST['gender']
        income = request.POST['income']
        expense = request.POST['expense']
        limit = request.POST['limit']

        profile.monthly_income = income
        profile.monthly_expense = expense
        profile.monthly_expense_limit = limit

        request.user.save()
        profile.save()
        return redirect('settings')

    return render(request, 'edit_profile.html', {'profile': profile})
