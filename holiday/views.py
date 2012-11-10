from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from holiday.models import Artist, Album, Classic, Song


class TitledListView(ListView):

    context_object_name = 'songs'
    paginate_by = 40
    template_name = 'songs.html'
    title = None

    def get_context_data(self, **kwargs):
        context = super(TitledListView, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class HomeView(ListView):

    queryset = Song.objects.select_related('album').order_by('-added', 'album', 'track')
    context_object_name = 'songs'
    paginate_by = 40
    template_name = 'home.html'


class ArtistView(DetailView):

    model = Artist
    context_object_name = 'artist'
    template_name = 'songs.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistView, self).get_context_data(**kwargs)
        query = Q(artist__slug=self.object.slug) | Q(album__artist__slug=self.object.slug)
        context['songs'] = Song.objects.filter(query).order_by('-added', 'album', 'track')
        return context


class AlbumView(DetailView):

    model = Album
    context_object_name = 'album'
    template_name = 'album.html'


class ClassicView(DetailView):

    model = Classic
    context_object_name = 'classic'
    template_name = 'songs.html'

    def get_context_data(self, **kwargs):
        context = super(ClassicView, self).get_context_data(**kwargs)
        context['songs'] = self.object.song_set.order_by('-added', 'album', 'track')
        return context


class CanPlayView(TitledListView):

    title = 'Playable'

    def get_queryset(self):
        qs = Song.objects.exclude(embed='')
        return qs.select_related('album').order_by('album__artist__name', 'album__title', 'track')


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
        context['title'] = u"Rated %s" % rated if self.RATINGS.index(rated) else u"Unrated"
        return context
