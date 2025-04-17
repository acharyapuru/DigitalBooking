from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlparse
from .models import UserProfile
from offer.models import UserRewardWallet, Gems, Points
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

User = get_user_model()
# Create your views here.

class RegisterView(View):

    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, "You are already logged in")
            return redirect("index")
        
        return render(request, "login.html")
    
    def post(self, request):
        next_url = request.POST.get("next") or "index"
        if request.user.is_authenticated:
            messages.error(request, "You are already logged in")
            return redirect("index")
        
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("cnfm-password")

        if password != confirm_password:
            messages.error(request, "Password do not match")
            return redirect("user:register")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists")
            return redirect("user:register")
        
        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        messages.success(request, "User created successfully")

        parsed_url = urlparse(next_url)
        path_only = parsed_url.path if parsed_url.netloc else next_url
        if path_only and url_has_allowed_host_and_scheme(path_only, settings.ALLOWED_HOSTS):
            return redirect(path_only)
        return redirect(reverse_lazy("index"))


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, "You are already logged in")
            return redirect("index")
        return render(request, "login.html")
    
    def post(self, request):
        next_url = request.POST.get("next") or "index"
        if request.user.is_authenticated:
            messages.error(request, "You are already logged in")
            return redirect("index")
        
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            messages.error(request, "Invalid credentials")
            return redirect("user:login")
        
        login(request, user)
        
        messages.success(request, "Logged in successfully")

        parsed_url = urlparse(next_url)
        path_only = parsed_url.path if parsed_url.netloc else next_url
        if path_only and url_has_allowed_host_and_scheme(path_only, settings.ALLOWED_HOSTS):
            return redirect(path_only)
        return redirect(reverse_lazy("index"))
    


def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect("index")
    else:
        messages.error(request, "You are not logged in")
        return redirect("user:login")
    

class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You are not logged in")
            return redirect("user:login")
        profile = UserProfile.objects.get(user=request.user)
        gem_content_type = ContentType.objects.get_for_model(Gems)
        point_content_type = ContentType.objects.get_for_model(Points)

        total_gems = UserRewardWallet.objects.filter(
            user=profile,
            content_type=gem_content_type
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        total_points = UserRewardWallet.objects.filter(
            user=profile,
            content_type=point_content_type
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        context = {
            "profile": profile,
            "gems": total_gems,
            "points": total_points
        }
        print(context)
        return render(request, "user/profile.html", context)