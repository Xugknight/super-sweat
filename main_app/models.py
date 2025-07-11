import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  display_name = models.CharField(max_length=100)
  rank = models.CharField(max_length=50, blank=True)
  main_game = models.CharField(max_length=100, blank=True)
  preferred_roles = models.CharField(max_length=100, blank=True)
  last_login = models.DateTimeField(blank=True, null=True)
  status = models.CharField(
      max_length=10,
      choices=[
          ('ACTIVE','Active'),
          ('INACTIVE','Inactive'),
      ],
      default='ACTIVE'
  )
  steam_id = models.CharField(max_length=50, blank=True, help_text="Your 64-bit SteamID")
  steam_profile = models.URLField(blank=True, help_text="Full Steam Community URL")
  discord_tag = models.CharField(max_length=32, blank=True, help_text="e.g. User#1234")
  twitch_channel = models.URLField(blank=True)
  created_at = models.DateTimeField(default=timezone.now, editable=False)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f"{self.display_name} ({self.user.username})"

class Guild(models.Model):
  name = models.CharField(max_length=50, unique=True)
  description = models.TextField(max_length=250, blank=True)
  owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='owned_guilds')
  created_at = models.DateTimeField(default=timezone.now, editable=False)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return self.name
  
class Membership(models.Model):
    ROLE_CHOICES = [
        ('LEADER','Guild Leader'),
        ('OFFICER','Officer'),
        ('MEMBER','Member'),
        ('RECRUIT','Recruit'),
        ('TRIAL','Trial'),
    ]
    guild = models.ForeignKey('Guild', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TRIAL')
    joined_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('guild','profile')

    def __str__(self):
        return f"{self.profile} in {self.guild} as {self.role}"

    Guild.add_to_class('members', models.ManyToManyField(
    Profile,
    through='Membership',
    related_name='guilds'
))

class EventTemplate(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    default_time = models.DurationField(help_text="Default duration (e.g. 2 hours)")
    default_roles = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated slots: e.g. DPS,Healer,Tank"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guild.name} · {self.name}"
    
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='events')
    template = models.ForeignKey(EventTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    required_roles = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated list of needed roles"
    )
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(
        max_length=200, 
        blank=True,
        help_text="iCal RRULE string if recurring"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} @ {self.start_time:%b %d, %Y %H:%M}"

class RSVP(models.Model):
    RESPONSE_CHOICES = [
        ('YES','Yes'),
        ('NO','No'),
        ('MAYBE','Maybe'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    response = models.CharField(max_length=5, choices=RESPONSE_CHOICES)
    role_signed_up = models.CharField(
        max_length=50,
        blank=True,
        help_text="The role this member plans to fill (e.g. DPS)"
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event','profile')

    def __str__(self):
        return f"{self.profile} → {self.event}: {self.response}"
    
class ExternalAccount(models.Model):
    SERVICE_CHOICES = [
        ('STEAM',   'Steam'),
        ('DISCORD', 'Discord'),
        ('TWITCH',  'Twitch'),
        ('OTHER',   'Other'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='external_accounts')
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    identifier = models.CharField(
        max_length=100,
        help_text="Could be a username, ID, or full URL"
    )
    url = models.URLField(
        blank=True,
        help_text="Full profile link (if applicable)"
    )

    class Meta:
        unique_together = ('profile','service','identifier')

    def __str__(self):
        return f"{self.profile.display_name} on {self.get_service_display()}"