from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),

    # Profile
    path('profiles/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profiles/edit/', views.ProfileUpdate.as_view(), name='profile-edit'),
    path('profiles/delete/', views.ProfileDelete.as_view(), name='profile-delete'),

    # Guilds
    path('guilds/', views.GuildList.as_view(), name='guild-list'),
    path('guilds/create/', views.GuildCreate.as_view(), name='guild-create'),
    path('guilds/<int:pk>/join/', views.guild_join, name='guild-join'),
    path('guilds/<int:pk>/leave/', views.guild_leave, name='guild-leave'),
    path('guilds/<int:pk>/templates/create/', views.EventTemplateCreate.as_view(), name='eventtemplate-create'),
    path('guilds/<int:pk>/events/create/', views.EventCreate.as_view(), name='event-create'),
    path('guilds/<int:pk>/', views.GuildDetail.as_view(), name='guild-detail'),
    path('guilds/<int:pk>/edit/', views.GuildUpdate.as_view(), name='guild-update'),
    path('guilds/<int:pk>/delete/', views.GuildDelete.as_view(), name='guild-delete'),
]
