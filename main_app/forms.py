from django import forms
from .models import Profile, Event

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
    save_as_template = forms.BooleanField(
        required= False,
        label= 'save these settings as the template' 
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
        ]

        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }