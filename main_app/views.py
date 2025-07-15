from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Profile, Guild, Membership, Event, EventTemplate, RSVP
from .forms import ProfileForm, EventCreateForm, RSVPform

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
        today = timezone.localtime()
        upcoming = self.object.events.filter(start_time__date__gte=today)
        data['upcoming_events'] = upcoming
        data['has_upcoming'] = upcoming.exists()
        annotated = []
        profile = self.request.user.profile
        for event in upcoming:
            event.count_yes = event.rsvps.filter(response='YES').count()
            event.count_no = event.rsvps.filter(response='NO').count()
            event.count_maybe = event.rsvps.filter(response='MAYBE').count()
            my_rsvp = RSVP.objects.filter(event=event, profile=profile).first()
            event.rsvp_form = RSVPform(instance=my_rsvp)
            annotated.append(event)
        all_memberships = self.object.membership_set.all()
        data['approved_members'] = all_memberships.filter(status='APPROVED')
        data['pending_members'] = all_memberships.filter(status='PENDING')
        data['is_approved'] = data['approved_members'].filter(profile=self.request.user.profile).exists()
        data['is_pending'] = data['pending_members'].filter(profile=self.request.user.profile).exists()
        is_owner = (profile == self.object.owner)
        is_officer = all_memberships.filter(profile=profile, role__in=('LEADER', 'OFFICER')).exists()
        data['can_manage_events'] = is_owner or is_officer
        data['role_choices'] = Membership.ROLE_CHOICES
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
        membership, created = Membership.objects.update_or_create(guild=guild, profile=request.user.profile, defaults={'status': Membership.STATUS_PENDING})
    return redirect('guild-detail', pk=pk)

@login_required
def guild_leave(request, pk):
    if request.method == 'POST':
        membership = get_object_or_404(Membership, guild__pk=pk, profile=request.user.profile)
        membership.delete()
    return redirect('guild-detail', pk=pk)

@login_required
def membership_approve(request, pk, mid):
    guild = get_object_or_404(Guild, pk=pk)
    profile = request.user.profile
    is_owner = profile == guild.owner
    is_officer = Membership.objects.filter(guild=guild, profile=profile, role='OFFICER').exists()
    if request.method == 'POST' and (is_owner or is_officer):
        memb = get_object_or_404(Membership, pk=mid, guild=guild, status=Membership.STATUS_PENDING)
        memb.status = Membership.STATUS_APPROVED
        memb.role = 'MEMBER'
        memb.save()
    return redirect('guild-detail', pk=pk)

@login_required
def membership_reject(request, pk, mid):
    guild = get_object_or_404(Guild, pk=pk)
    profile = request.user.profile
    is_owner = profile == guild.owner
    is_officer = Membership.objects.filter(guild=guild, profile=profile, role='OFFICER').exists()
    if request.method == 'POST' and (is_owner or is_officer):
        Membership.objects.filter(pk=mid, guild=guild, status=Membership.STATUS_PENDING).delete()
    return redirect('guild-detail', pk=pk)

def membership_update_role(request, pk, mid):
    guild = get_object_or_404(Guild, pk=pk)
    profile = request.user.profile
    if request.method == 'POST' and profile == guild.owner:
        m = get_object_or_404(Membership, pk=mid, guild=guild, status='APPROVED')
        new_role = request.POST.get('role')
        if new_role in dict(Membership.ROLE_CHOICES):
            m.role = new_role
            m.save()
        return redirect('guild-detail', pk=pk)

class EventCreate(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'events/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.guild = get_object_or_404(Guild, pk=kwargs['pk'])
        profile = request.user.profile
        is_owner = (profile == self.guild.owner)
        is_member = Membership.objects.filter(
            guild = self.guild,
            profile = request.user.profile,
            status = Membership.STATUS_APPROVED
        ).exists()
        if not (is_owner or is_member):
            raise PermissionDenied('You must be a guild member to schedule events.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['template'].queryset = self.guild.templates.all()
        return form
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['guild'] = self.guild
        return ctx

    def form_valid(self, form):
        tpl = form.cleaned_data.get('template')
        if tpl:
            form.instance.title = tpl.name
            form.instance.required_roles = tpl.default_roles
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

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_object()
        self.guild = self.event.guild
        profile = request.user.profile
        is_owner = (profile == self.guild.owner)
        is_officer = Membership.objects.filter(
            guild=self.guild,
            profile=profile,
            role__in=('LEADER','OFFICER'),
            status=Membership.STATUS_APPROVED
        ).exists()
        if not (is_owner or is_officer):
            raise PermissionDenied('You aren’t allowed to edit this event.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['guild'] = self.guild
        return ctx

    def form_valid(self, form):
        event = form.save()
        if form.cleaned_data.get('save_as_template'):
            EventTemplate.objects.update_or_create(
                guild=self.guild,
                name=event.title,
                defaults={
                    'default_time': event.end_time - event.start_time,
                    'default_roles': event.required_roles
                }
            )
        return redirect('guild-detail', pk=self.guild.pk)

class EventDelete(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        guild = event.guild
        profile = request.user.profile
        is_owner = (profile == guild.owner)
        is_officer = Membership.objects.filter(
            guild=guild,
            profile=profile,
            role__in=('LEADER','OFFICER'),
            status=Membership.STATUS_APPROVED
        ).exists()
        if not (is_owner or is_officer):
            raise PermissionDenied('You aren’t allowed to edit this event.')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        event = self.get_object()
        guild_pk = event.guild.pk
        event.delete()
        return redirect('guild-detail', pk=guild_pk)

class EventDetail(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'

@login_required
def rsvp(request, pk):
    event = get_object_or_404(Event, pk=pk)
    profile = request.user.profile
    guild = event.guild
    is_owner = profile == guild.owner
    is_officer = Membership.objects.filter(
            guild=guild,
            profile=profile,
            role__in=('LEADER','OFFICER'),
            status=Membership.STATUS_APPROVED
        ).exists()
    is_member = Membership.objects.filter(
            guild=guild,
            profile=profile,
            status=Membership.STATUS_APPROVED
        ).exists()
    if not (is_owner or is_officer or is_member):
        raise PermissionDenied('Only Guild Members can RSVP')
    rsvp, _ = RSVP.objects.get_or_create(event=event, profile=profile)
    if request.method == 'POST': 
        form = RSVPform(request.POST, instance=rsvp)
        if form.is_valid():
            form.save()
    return redirect ('guild-detail', pk=guild.pk)