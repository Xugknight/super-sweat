from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Profile, Guild, Membership, Event, EventTemplate
from .forms import ProfileForm, EventCreateForm

class Home(LoginView):
    template_name = 'home.html'

def signup(request):
    error = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, display_name=user.username)
            login(request, user)
            return redirect('profile-detail')
        error = 'Invalid signup, please try again.'
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'error': error})

def about(request):
    return render(request, 'about.html')

class ProfileDetail(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/detail.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/form.html'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        form.save()
        return redirect('profile-detail')

class ProfileDelete(LoginRequiredMixin, DeleteView):
    model = Profile
    template_name = 'profiles/confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        logout(request)
        user = profile.user
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
        now = timezone.now()
        upcoming = self.object.events.filter(start_time__gte=now)
        data['upcoming_events'] = upcoming
        data['has_upcoming'] = upcoming.exists()

        profile = self.request.user.profile
        is_owner = (profile == self.object.owner)
        membership = Membership.objects.filter(guild=self.object, profile=profile).first()
        is_officer = membership and membership.role in ('LEADER', 'OFFICER')
        data['can_manage_events'] = is_owner or is_officer
        return data

class GuildCreate(LoginRequiredMixin, CreateView):
    model = Guild
    fields = ['name', 'description']
    template_name = 'guilds/form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('guild-detail', kwargs={'pk': self.object.pk})

class GuildUpdate(LoginRequiredMixin, UpdateView):
    model = Guild
    fields = ['name', 'description']
    template_name = 'guilds/form.html'

    def get_queryset(self):
        return Guild.objects.filter(owner=self.request.user.profile)

    def get_success_url(self):
        return reverse('guild-detail', kwargs={'pk': self.object.pk})

class GuildDelete(LoginRequiredMixin, DeleteView):
    model = Guild
    template_name = 'guilds/confirm_delete.html'
    success_url = reverse_lazy('guild-list')

    def get_queryset(self):
        return Guild.objects.filter(owner=self.request.user.profile)

@login_required
def guild_join(request, pk):
    if request.method == 'POST':
        guild = get_object_or_404(Guild, pk=pk)
        Membership.objects.get_or_create(guild=guild, profile=request.user.profile, defaults={'role': 'MEMBER'})
    return redirect('guild-detail', pk=pk)

@login_required
def guild_leave(request, pk):
    if request.method == 'POST':
        membership = get_object_or_404(Membership, guild__pk=pk, profile=request.user.profile)
        membership.delete()
    return redirect('guild-detail', pk=pk)

class EventCreate(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'events/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.guild = get_object_or_404(Guild, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        event = form.save(commit=False)
        event.guild = self.guild
        event.save()
        if form.cleaned_data.get('save_as_template'):
            EventTemplate.objects.create(
                guild=self.guild,
                name=event.title,
                default_time=event.end_time - event.start_time,
                default_roles=event.required_roles
            )
        return redirect('guild-detail', pk=self.guild.pk)

class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'events/form.html'

    def form_valid(self, form):
        event = form.save()
        if form.cleaned_data.get('save_as_template'):
            EventTemplate.objects.update_or_create(
                guild=event.guild,
                name=event.title,
                defaults={
                    'default_time': event.end_time - event.start_time,
                    'default_roles': event.required_roles
                }
            )
        return redirect('guild-detail', pk=event.guild.pk)

class EventDelete(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        guild_pk = event.guild.pk
        event.delete()
        return redirect('guild-detail', pk=guild_pk)

class EventDetail(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'