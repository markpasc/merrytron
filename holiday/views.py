from __future__ import unicode_literals

from django.db.models import Q, Max
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView

from holiday.models import Artist, Album, Classic, Song


class HomeView(ListView):

    queryset = Album.objects.exclude(artwork='').order_by('-id')[:8]
    context_object_name = 'albums'
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['latest_date'] = Song.objects.all().aggregate(Max('added'))['added__max']
        return context


class TitledListView(ListView):

    context_object_name = 'songs'
    paginate_by = 40
    template_name = 'songs.html'
    title = None

    def get_context_data(self, **kwargs):
        context = super(TitledListView, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class RecentView(TitledListView):

    queryset = Song.objects.select_related('album').order_by('-added', 'album', 'track')
    title = 'Recently added'


class ArtistView(DetailView):

    model = Artist
    context_object_name = 'artist'
    template_name = 'songs.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        query = Q(artist__slug=self.object.slug) | Q(album__artist__slug=self.object.slug)
        context['songs'] = Song.objects.filter(query).select_related('album').order_by('album__title', 'track')
        return context


class AlbumView(DetailView):

    model = Album
    context_object_name = 'album'
    template_name = 'album.html'


class ClassicListView(ListView):

    model = Classic
    context_object_name = 'classics'
    template_name = 'classics.html'


class ClassicView(DetailView):

    model = Classic
    context_object_name = 'classic'
    template_name = 'songs.html'

    def get_context_data(self, **kwargs):
        context = super(ClassicView, self).get_context_data(**kwargs)
        context['songs'] = self.object.song_set.order_by('-added', 'album', 'track')
        return context


class NontradView(TitledListView):

    queryset = Song.objects.filter(classic=None).select_related('album').order_by('album__artist__name', 'album__title', 'track')
    title = 'Non-traditional'


class AlphaView(TitledListView):

    queryset = Song.objects.select_related('album').order_by('album__artist__name', 'album__title', 'track')
    title = 'All songs'
    paginate_by = 50
    paginate_orphans = 5


class PlayableView(TitledListView):

    queryset = Song.objects.exclude(embed='').select_related('album').order_by('album__artist__name', 'album__title', 'track')
    title = 'Playable streams'


class DownloadView(TitledListView):

    title = 'Free downloads'

    def get_queryset(self):
        song_query = Q(price='') & ~Q(buy_link='')
        album_query = Q(album__price='') & ~Q(album__buy_link='')
        query = song_query | album_query
        qs = Song.objects.filter(query)
        return qs.select_related('album').order_by('album__artist__name', 'album__title', 'track')


class RatedView(ListView):

    paginate_by = 40
    context_object_name = 'songs'
    template_name = 'songs.html'

    RATINGS = ('unrated', 'good', 'great', 'best')

    def get_queryset(self):
        rated = self.kwargs['rated']
        rating = self.RATINGS.index(rated)
        qs = Song.objects.filter(rating=rating)
        return qs.select_related('album').order_by('album__artist__name', 'album__title', 'track')

    def get_context_data(self, **kwargs):
        context = super(RatedView, self).get_context_data(**kwargs)
        rated = self.kwargs['rated']
        context['title'] = "Rated %s" % rated if self.RATINGS.index(rated) else "Unrated"
        return context


class SearchView(TitledListView):

    context_object_name = 'songs'
    template_name = 'songs.html'
    paginate_by = None

    def get_queryset(self):
        self.query = self.request.GET.get('q')
        return Song.objects.raw("""
            SELECT *
              FROM holiday_song
             WHERE search_content @@ plainto_tsquery('english', %s)
        """, [self.query])

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['title'] = "Search for “{}”".format(self.query)
        return context


class ErrorPageView(TemplateView):

    template_name = '500.html'
