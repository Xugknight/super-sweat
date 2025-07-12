from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('profiles/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profiles/edit/', views.ProfileUpdate.as_view(), name='profile-edit'),
    path('profiles/delete/', views.ProfileDelete.as_view(), name='profile-delete'),
    path('accounts/signup/', views.signup, name='signup'),
    path('guilds/', views.GuildList.as_view(), name='guild-list'),
    path('guilds/<int:pk>', views.GuildDetail.as_view(), name='guild-detail'),
]