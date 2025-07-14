from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),

    # Profile
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/edit/', views.ProfileUpdate.as_view(), name='profile-edit'),
    path('profile/delete/', views.ProfileDelete.as_view(), name='profile-delete'),

    # Guild
    path('guilds/', views.GuildList.as_view(), name='guild-list'),
    path('guilds/create/', views.GuildCreate.as_view(), name='guild-create'),
    path('guilds/<int:pk>/', views.GuildDetail.as_view(), name='guild-detail'),
    path('guilds/<int:pk>/edit/', views.GuildUpdate.as_view(), name='guild-update'),
    path('guilds/<int:pk>/delete/', views.GuildDelete.as_view(), name='guild-delete'),
    path('guilds/<int:pk>/join/', views.guild_join, name='guild-join'),
    path('guilds/<int:pk>/leave/', views.guild_leave, name='guild-leave'),

    # Events
    path('guilds/<int:pk>/events/create/', views.EventCreate.as_view(), name='event-create'),
    path('events/<uuid:pk>/', views.EventDetail.as_view(), name='event-detail'),
    path('events/<uuid:pk>/edit/', views.EventUpdate.as_view(), name='event-update'),
    path('events/<uuid:pk>/delete/', views.EventDelete.as_view(), name='event-delete'),
]