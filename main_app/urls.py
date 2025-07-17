from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    # Profile
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/edit/', views.ProfileUpdate.as_view(), name='profile-edit'),
    path('profile/delete/', views.ProfileDelete.as_view(), name='profile-delete'),
    path('profiles/<int:pk>/', views.ProfilePublicDetail.as_view(), name='profile-public'),
    path('profiles/external/<int:pk>/delete/', views.ExternalAccountDelete.as_view(), name='external-delete'),

    # Guild
    path('guilds/', views.GuildList.as_view(), name='guild-list'),
    path('guilds/create/', views.GuildCreate.as_view(), name='guild-create'),
    path('guilds/<int:pk>/', views.GuildDetail.as_view(), name='guild-detail'),
    path('guilds/<int:pk>/edit/', views.GuildUpdate.as_view(), name='guild-update'),
    path('guilds/<int:pk>/delete/', views.GuildDelete.as_view(), name='guild-delete'),
    path('guilds/<int:pk>/join/', views.guild_join, name='guild-join'),
    path('guilds/<int:pk>/leave/', views.guild_leave, name='guild-leave'),
    path('guilds/<int:pk>/membership/<int:mid>/approve/', views.membership_approve, name='membership-approve'),
    path('guilds/<int:pk>/membership/<int:mid>/reject/', views.membership_reject, name='membership-reject'),
    path('guilds/<int:pk>/membership/<int:mid>/role/', views.membership_update_role, name='membership-update-role'),

    # Events
    path('guilds/<int:pk>/events/create/', views.EventCreate.as_view(), name='event-create'),
    path('events/<uuid:pk>/', views.EventDetail.as_view(), name='event-detail'),
    path('events/<uuid:pk>/edit/', views.EventUpdate.as_view(), name='event-update'),
    path('events/<uuid:pk>/delete/', views.EventDelete.as_view(), name='event-delete'),
    path('events/<uuid:pk>/rsvp/', views.rsvp, name='rsvp'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT,
    )