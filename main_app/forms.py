from django import forms
from .models import Profile, Event, EventTemplate, RSVP

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'rank',
            'main_game',
            'preferred_roles',
            'status',
        ]
        widgets = {
            'preferred_roles': forms.TextInput(attrs={'placeholder': 'e.g. DPS,Healer'}),
            'status': forms.Select(),
        }

class EventCreateForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=EventTemplate.objects.none(),
        required=False,
        label = 'Use existing template'
    )
    save_as_template = forms.BooleanField(
        required= False,
        label= 'save this event as a new template' 
    )        
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'start_time',
            'end_time',
            'required_roles',
            'max_participants',
            'template',
            'save_as_template'
        ]

        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RSVPform(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = [
            'response',
            'role_signed_up',    
        ]

        widgets = {
            'response': forms.Select(),
            'role_signed_up': forms.TextInput(attrs={'placeholder': 'dps-tank-heal','class': 'form-control'}),
        }