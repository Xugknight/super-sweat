from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('profile/<int:profile_id>', views.profile_detail, name='profile-detail'),
    path('accounts/signup/', views.signup, name='signup'),
    path('guilds/', views.guild_index, name='guild-index'),
]