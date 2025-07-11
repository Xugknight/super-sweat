import requests
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Profile, Guild
# Import HttpResponse to send text-based responses


# Define the home view function
class Home(LoginView):
    template_name = 'home.html'

def about(request):
    return render(request, 'about.html')

def profile_detail(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    return render(request, 'detail.html', {'profile': profile})

def guild_index(request, guild_id):
    guild = Guild.objects.get(id=guild_id)
    return render (request, 'index.html', {'guild': guild})

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error-message': error_message}
    return render(request, 'signup.html', context)