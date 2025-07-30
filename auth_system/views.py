from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("main:home")
            else:
                messages.error(request, "❌ Invalid username or password.")
        else:
            messages.error(request, "⚠️ Invalid input.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def home_auth(request):
    return render(request, 'registration/home_auth.html')


def logout_view(request):
    logout(request)
    return redirect("login")
