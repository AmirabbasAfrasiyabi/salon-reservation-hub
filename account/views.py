from django.shortcuts import render ,redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random
from .models import User,CustomerProfile,StylistProfile,SalonOwnerProfile,OTPCode


# Create your views here.
# ================== ثبت‌نام و ورود ==================

def register_view(request, generate_otp=None):
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')

        if password != password2:
            messages.error(request,'Passwords do not match')
            return render(request, 'account/register.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request,'Phone number already exists')
            return render(request, 'account/register.html')

        user = User.objects.create_user(username=username,email=email,password=password)

        otp_code = generate_otp(phone_number)

        messages.success(request,'OTP code has been sent successfully')
        return redirect('account:verify_phone_number',user_id=user.id)

    return render(request, 'account/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request,f'wellcome{user.get_full_name()}')

            next_url = request.GET.get('next' , 'account:dashboard')
            return redirect(next_url)
        else:
            messages.error(request,'Invalid username or password')

    return render(request, 'account/login.html')
