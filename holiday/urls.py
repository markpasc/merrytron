from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView

from holiday import views
from holiday import models


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
        queryset=models.Song.objects.select_related('album').order_by('-added', 'album', 'track')[:40],
        context_object_name='songs',
        template_name='home.html',
    ), name='home'),
    url(r'^artist/(?P<slug>.*)$', views.ArtistView.as_view(
        template_name='songs.html',
    ), name='artist'),
    url(r'^album/(?P<slug>.*)$', DetailView.as_view(
        model=models.Album,
        context_object_name='album',
        template_name='album.html',
    ), name='album'),

    url(r'^classic/(?P<slug>.*)$', views.ClassicView.as_view(
        template_name='songs.html',
    ), name='classic'),

    url(r'^rating/good$', views.TitledListView.as_view(
        queryset=models.Song.objects.filter(rating=1).select_related('album').order_by('-added', 'album', 'track'),
        title='Rated good',
    ), name='good'),
    url(r'^rating/great$', views.TitledListView.as_view(
        queryset=models.Song.objects.filter(rating=2).select_related('album').order_by('-added', 'album', 'track'),
        title='Rated great',
    ), name='great'),
    url(r'^rating/best$', views.TitledListView.as_view(
        queryset=models.Song.objects.filter(rating=3).select_related('album').order_by('-added', 'album', 'track'),
        title='Rated best',
    ), name='best'),
)
