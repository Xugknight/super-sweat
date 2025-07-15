from django import forms
from .models import Profile, Event, EventTemplate

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

    def __init__(self, *args, guild=None, **kwargs):
        guild = kwargs.pop('guild', None)
        print("🔍 [EventCreateForm] __init__  guild:", guild)
        super().__init__(*args, **kwargs)
        if guild is not None:
            qs = guild.templates.all()
            print("🔍 [EventCreateForm] templates:", list(qs.values_list('pk','name')))
            self.fields['template'].queryset = qs
            self.fields['template'].queryset = guild.templates.all()
        tpl_pk = self.data.get('template') or self.initial.get('template')
        if tpl_pk and guild is not None:
            try:
                tpl = guild.templates.get(pk=tpl_pk)
                self.fields['title'].initial = tpl.name
                self.fields['required_roles'].initial = tpl.default_roles
            except EventTemplate.DoesNotExist:
                pass

        