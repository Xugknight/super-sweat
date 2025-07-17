import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    display_name = models.CharField(max_length=100)
    rank = models.CharField(max_length=50, blank=True)
    main_game = models.CharField(max_length=100, blank=True)
    preferred_roles = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('ACTIVE','Active'), ('INACTIVE','Inactive')],
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username

    def get_absolute_url(self):
        return reverse('profile-detail')

class Guild(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='owned_guilds')
    members = models.ManyToManyField(Profile, through='Membership', related_name='guilds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('guild-detail', kwargs={'pk': self.pk})

class Membership(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected')
    ]
    ROLE_CHOICES = [
        ('LEADER','Guild Leader'),
        ('OFFICER','Officer'),
        ('MEMBER','Member'),
        ('RECRUIT','Recruit'),
        ('TRIAL','Trial'),
    ]
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='RECRUIT')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('guild','profile')

    def __str__(self):
        return f"{self.profile.display_name} in {self.guild.name} as {self.get_role_display()} [{self.get_status_display()}]"

class EventTemplate(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=100)
    default_time = models.DurationField(help_text="Default duration, e.g. 2 hours")
    default_roles = models.CharField(max_length=200, blank=True, help_text="Comma-separated roles: DPS,Healer,Tank")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guild.name} · {self.name}"

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='events')
    template = models.ForeignKey(EventTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    required_roles = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of roles needed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} @ {self.start_time:%b %d, %Y %H:%M}"

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})

class RSVP(models.Model):
    RESPONSE_CHOICES = [
        ('YES','Yes'),
        ('NO','No'),
        ('MAYBE','Maybe'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    response = models.CharField(max_length=5, choices=RESPONSE_CHOICES)
    role_signed_up = models.CharField(max_length=50, blank=True, help_text="Role this member plans to fill, e.g. DPS")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event','profile')

    def __str__(self):
        return f"{self.profile.display_name} → {self.event.title}: {self.get_response_display()}"

class ExternalAccount(models.Model):
    SERVICE_CHOICES = [
        ('STEAM','Steam'),
        ('DISCORD','Discord'),
        ('TWITCH','Twitch'),
        ('OTHER','Other'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='external_accounts')
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    identifier = models.CharField(max_length=100, help_text="Username, ID, or full URL")
    url = models.URLField(blank=True, help_text="Full profile link if applicable")

    class Meta:
        unique_together = ('profile','service','identifier')

    def __str__(self):
        return f"{self.profile.display_name} on {self.get_service_display()}"

class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class ProfileRole(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile','role')

    def __str__(self):
        return f"{self.profile.display_name}: {self.role.name}"