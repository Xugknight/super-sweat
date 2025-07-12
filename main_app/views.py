import requests
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Profile, Guild
from .forms import ProfileForm

# Define the home view function
class Home(LoginView):
    template_name = 'home.html'

def about(request):
    return render(request, 'about.html')

class ProfileDetail(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/form.html'
    success_url = reverse_lazy('profile-detail')

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
    
class ProfileDelete(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'profiles/confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset = None):
        return Profile.objects.get(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        logout(request)
        profile.delete()
        user.delete()
        return super().delete(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Get the current user's profile and user object
        profile = self.get_object()
        user = request.user
        
        # Log the user out before deletion
        logout(request)

        # Delete the profile and user
        profile.delete()
        user.delete()
        return redirect(self.success_url)

        

def guild_index(request, guild_id):
    guild = Guild.objects.get(id=guild_id)
    return render (request, 'index.html', {'guild': guild})

def guild_detail(request, guild_id):
    guild = Guild.objects.get(id=guild_id)
    return render(request, 'detail.html', {'guild': guild})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, display_name=user.username)
            login(request, user)
            return redirect('profile-detail')  
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})
