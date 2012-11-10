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

    url(r'^rated/(?P<rated>unrated|good|great|best)/(?:page(?P<page>\d+))?$',
        views.RatedView.as_view(), name='rated'),
)
