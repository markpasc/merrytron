# coding=utf-8

from __future__ import unicode_literals

from datetime import date

from django.db import models, connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    num_songs = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @classmethod
    def bulk_update_num_songs(cls):
        artist_data = cls.objects.all().annotate(song_count=models.Count('song')).values('id', 'song_count')
        for artist in artist_data:
            cls.objects.filter(id=artist['id']).update(num_songs=artist['song_count'])

    class Meta:
        ordering = ('name',)


class Album(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    artist = models.ForeignKey(Artist, null=True, blank=True)
    artwork = models.ImageField(upload_to='artwork', blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)

    def __str__(self):
        if self.artist_id:
            return "%s – %s" % (self.title, self.artist.name)
        return self.title

    def songs(self):
        return self.song_set.all().order_by('track')

    def add_songs(self, songs, added=None):
        if added is None:
            added = date.today()
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

    def __str__(self):
        return self.title

    def merge_from(self, other):
        other_songs = other.song_set.all()
        other_songs.update(classic=self)
        other.delete()

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
    added = models.DateField(default=date.today)
    notes = models.TextField(blank=True)
    embed = models.TextField(blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)

    def __str__(self):
        if self.artist_id:
            return "%s – %s" % (self.title, self.artist.name)
        return self.title


@receiver(post_save, sender=Song)
@receiver(post_delete, sender=Song)
def update_song_artist_num_songs(sender, **kwargs):
    if kwargs.get('raw'):
        return
    artist = kwargs['instance'].artist
    num_songs = artist.song_set.count()
    if artist.num_songs != num_songs:
        artist.num_songs = num_songs
        artist.save()


@receiver(post_save, sender=Song)
def update_search_content(sender, **kwargs):
    song = kwargs['instance']
    artist_name = song.artist.name if song.artist_id else ''
    album_title = song.album.title if song.album_id else ''
    classic_title = song.classic.title if song.classic_id else ''

    cursor = connection.cursor()
    cursor.execute("""
        UPDATE holiday_song
           SET search_content = setweight(to_tsvector('english', title), 'A')
            || setweight(to_tsvector('english', %s), 'B')
            || setweight(to_tsvector('english', %s), 'B')
            || setweight(to_tsvector('english', buy_link), 'D')
            || setweight(to_tsvector('english', %s), 'D')
         WHERE id = %s
    """, [artist_name, album_title, classic_title, song.id])


def total_song_count_cp(request):
    return {
        'total_songs': lambda: Song.objects.all().count()
    }
