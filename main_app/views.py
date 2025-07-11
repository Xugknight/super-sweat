from django.shortcuts import render
from .models import Profile, Guild
# Import HttpResponse to send text-based responses


# Define the home view function
def home(request):
    # Send a simple HTML response
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def profile_detail(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    return render(request, 'detail.html', {'profile': profile})

def guild_index(request, guild_id):
    guild = Guild.objects.get(id=guild_id)
    return render (request, 'index.html', {'guild': guild})