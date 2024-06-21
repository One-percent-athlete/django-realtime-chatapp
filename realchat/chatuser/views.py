from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from allauth.account.utils import send_email_confirmation
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout

from .models import User
from .forms import ProfileForm, EmailForm

def view_profile(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect('account_login')
    return render(request, "users/profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES,instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
        
    if request.path == reverse("create_profile"):
        create_profile = True
    else:
        create_profile = False

    return render(request, "users/edit_profile.html", {"form": form, "create_profile":create_profile})

@login_required
def profile_settings(request):
    return render(request, 'users/profile_settings.html')

@login_required
def delete_profile(request):
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "See You Again..")
        return redirect('home')
    return render(request, 'users/delete_profile.html')


@login_required
def edit_email(request):
    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, "edit_email.html", {"form": form})
    
    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)
        if form.is_valid():

            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, "Email Already In Use..")
                return redirect('profile_settings')
            form.save()
            
            send_email_confirmation(request, request.user)
            return redirect('profile_settings')
        else:
            messages.warning(request, 'Invalid Form..')
            return redirect('profile_settings')
    return redirect('home')
            
@login_required
def verify_email(request):
    send_email_confirmation(request, request.user)
    return redirect('profile_settings')

