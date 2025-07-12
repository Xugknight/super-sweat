import requests
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Profile, Guild, Membership
from .forms import ProfileForm

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
        profile = self.get_object()
        user = request.user
        
        logout(request)

        profile.delete()
        user.delete()
        return redirect(self.success_url)

class GuildList(LoginRequiredMixin, ListView):
    model = Guild
    template_name = 'guilds/index.html'
    context_object_name = 'guilds'

class GuildDetail(LoginRequiredMixin, DetailView):
    model = Guild
    template_name = 'guilds/detail.html'
    context_object_name = 'guild'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['now'] = timezone.now()
        return data

class GuildCreate(LoginRequiredMixin, CreateView):
    model = Guild
    fields = ['name', 'description']
    template_name = 'guilds/form.html'
    success_url = reverse_lazy('guild-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)
    
class GuildUpdate(LoginRequiredMixin, UpdateView):
    model = Guild
    fields = ['name', 'description']
    template_name = 'guilds/form.html'
    success_url = reverse_lazy('guild-list')

    def get_queryset(self):
        return Guild.objects.filter(owner=self.request.user.profile)
    
class GuildDelete(LoginRequiredMixin, DeleteView):
    model = Guild
    template_name = 'guilds/confirm_delete.html'
    success_url = reverse_lazy('guild-list')

    def get_queryset(self):
        return Guild.objects.filter(owner=self.request.user.profile)

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

@login_required
def guild_join(request, pk):
    if request.method == 'POST':
        guild = get_object_or_404(Guild, pk=pk)
        profile = request.user.profile

        Membership.objects.get_or_create(
            guild=guild,
            profile=profile,
            defaults={'role': 'MEMBER'}
        )
    return redirect('guild-detail', pk=pk)