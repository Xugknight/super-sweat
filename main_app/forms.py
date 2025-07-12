from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'rank',
            'main_game',
            'preferred_roles',
            'steam_id',
            'steam_profile',
            'discord_tag',
            'twitch_channel',
            'status',
        ]
        widgets = {
            'preferred_roles': forms.TextInput(attrs={'placeholder': 'e.g. DPS,Healer'}),
            'status': forms.Select(),
        }