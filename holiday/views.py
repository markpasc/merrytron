from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from holiday.models import Artist, Song


class ArtistView(DetailView):

	model = Artist
	context_object_name = 'artist'

	def get_context_data(self, **kwargs):
		context = super(ArtistView, self).get_context_data(**kwargs)
		query = Q(artist__slug=self.object.slug) | Q(album__artist__slug=self.object.slug)
		context['songs'] = Song.objects.filter(query).order_by('-added', 'album', 'track')
		return context
