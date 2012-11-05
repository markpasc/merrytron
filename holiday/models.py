from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, null=True, blank=True)
    artwork = models.ImageField(upload_to='artwork', null=True, blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)

    @property
    def is_compilation(self):
        return self.artist is None


class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist)
    rating = models.PositiveSmallIntegerField(blank=True, default=0)
    genre = models.CharField(max_length=20, blank=True)
    added = models.DateField()
    notes = models.TextField(blank=True)
    embed = models.TextField(blank=True)
    buy_link = models.URLField(blank=True)
    price = models.CharField(max_length=10, blank=True)
