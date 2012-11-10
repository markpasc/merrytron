from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView

from holiday import views
from holiday import models


urlpatterns = patterns('',
    url(r'^(?:page(?P<page>\d+))?$', views.HomeView.as_view(), name='home'),
    url(r'^artist/(?P<slug>.*)$', views.ArtistView.as_view(), name='artist'),
    url(r'^album/(?P<slug>.*)$', views.AlbumView.as_view(), name='album'),
    # everything

    url(r'^classic/(?P<slug>.*)$', views.ClassicView.as_view(), name='classic'),
    # has embed
    # free downloads
    # genre?

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
