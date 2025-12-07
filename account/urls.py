from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path("verify/", views.verify_phone_number, name="verify_phone"),
    path('resend_otp/' , views.resend_otp , name="resend_otp"),

]