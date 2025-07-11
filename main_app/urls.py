from django.urls import path
from . import views # Import views to connect routes to view functions

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('home/', views.home, name='home'),
    path('profile/<int:profile_id>', views.profile_detail, name='profile-detail'),
    path('guilds/', views.guild_index, name='guild-index'),
]