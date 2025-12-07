from django.contrib.auth.decorators import login_required
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

@login_required
def logout_view(request):
    logout(request)
    messages.success(request,'logout seccessfully')
    return redirect('home')



@login_required
def verify_phone_number(request):
    user = request.user

    # اگر قبلاً تایید شده باشد
    if user.is_phone_verified:
        messages.info(request, 'شماره موبایل شما قبلاً تایید شده است.')
        return redirect('account:login')

    if request.method == 'POST':
        code = request.POST.get('code')

        try:
            otp = OTPCode.objects.get(
                phone_number=user.phone_number,
                code=code,
                is_used=False
            )

            if otp.is_expired():
                messages.error(request, 'کد تایید منقضی شده است.')
                return render(request, 'accounts/verify_phone.html', {'user': user})

            # تایید شماره
            user.is_phone_verified = True
            user.save()

            otp.is_used = True
            otp.save()

            messages.success(request, 'شماره موبایل شما با موفقیت تایید شد.')
            return redirect('account:login')

        except OTPCode.DoesNotExist:
            messages.error(request, 'کد تایید اشتباه است.')

    return render(request, 'accounts/verify_phone.html', {'user': user})


@login_required
def resend_otp(request):
    user = request.user

    # ساخت OTP جدید
    OTPCode.objects.create(phone_number=user.phone_number)

    return JsonResponse({"success": True})