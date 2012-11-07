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
        template_name='artist.html',
    ), name='artist'),
)
