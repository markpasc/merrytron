from django.contrib import admin

from holiday.models import Artist, Album, Song


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Artist, ArtistAdmin)


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist')
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Album, AlbumAdmin)


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'track', 'album', 'rating', 'added')

admin.site.register(Song, SongAdmin)
