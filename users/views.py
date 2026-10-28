
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Registration successful! Please log in."
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(
        request,
        "users/register.html",
        {"form": form}
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )
            return redirect("home")

        messages.error(
            request,
            "Invalid username or password. Please register first or check your details."
        )

    return render(request, "users/login.html")


def user_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have logged out successfully.")

    return redirect("login")


@login_required
def home(request):
    return render(request, "users/home.html")


@login_required
def about(request):
    return render(request, "users/about.html")


@login_required
def profile(request):
    return render(request, "users/profile.html")
