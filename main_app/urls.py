from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('profiles/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('accounts/signup/', views.signup, name='signup'),
    path('guilds/', views.guild_index, name='guild-index'),
    path('guilds/', views.guild_detail, name='guild-detail'),
]