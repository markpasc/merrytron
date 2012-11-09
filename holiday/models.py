# coding=utf-8

from datetime import date

from django.db import models
from django.template.defaultfilters import slugify


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Album(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    artist = models.ForeignKey(Artist, null=True, blank=True)
    artwork = models.ImageField(upload_to='artwork', null=True, blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)

    def __unicode__(self):
        if self.artist_id:
            return u"%s — %s" % (self.title, self.artist.name)
        return self.title

    def songs(self):
        return self.song_set.all().order_by('track')

    def add_songs(self, songs, added=None):
        if added is None:
            added = date(2010, 10, 31)
        for song in songs:
            track, title, artistname, rating, classicname = song

            if artistname is None:
                artist = self.artist
            else:
                artist, _ = Artist.objects.get_or_create(name=artistname,
                    defaults={'slug': slugify(artistname)})

            classic = None
            if classicname is not None:
                if classicname is True:
                    classicname = title
                classic, _ = Classic.objects.get_or_create(title=classicname,
                    defaults={'slug': slugify(classicname)})

            obj = Song(title=title, album=self, artist=artist, track=track, added=added,
                rating=rating or 0, classic=classic)
            obj.save()

    @property
    def is_compilation(self):
        return self.artist is None

    class Meta:
        ordering = ('title',)


class Classic(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist)
    album = models.ForeignKey(Album, null=True, blank=True)
    track = models.PositiveIntegerField(null=True, blank=True)
    classic = models.ForeignKey(Classic, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(blank=True, default=0)
    genre = models.CharField(max_length=20, blank=True)
    added = models.DateField()
    notes = models.TextField(blank=True)
    embed = models.TextField(blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)

    def __unicode__(self):
        if self.artist_id:
            return u"%s — %s" % (self.title, self.artist.name)
        return self.title
