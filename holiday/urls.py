from django.conf.urls import patterns, url

from holiday import views
from holiday import models


urlpatterns = patterns('',
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^recent/(?:page(?P<page>\d+))?$', views.RecentView.as_view(), name='recent'),
    url(r'^artist/(?P<slug>.*)$', views.ArtistView.as_view(), name='artist'),
    url(r'^album/(?P<slug>.*)$', views.AlbumView.as_view(), name='album'),
    # everything

    url(r'^all/(?:page(?P<page>\d+))?$', views.AlphaView.as_view(), name='alpha'),
    url(r'^classic/(?P<slug>.*)$', views.ClassicView.as_view(), name='classic'),
    url(r'^playable/(?:page(?P<page>\d+))?$', views.PlayableView.as_view(), name='playable'),
    url(r'^downloads/(?:page(?P<page>\d+))?$', views.DownloadView.as_view(), name='download'),
    # genre?

    url(r'^rated/(?P<rated>unrated|good|great|best)/(?:page(?P<page>\d+))?$',
        views.RatedView.as_view(), name='rated'),
)
