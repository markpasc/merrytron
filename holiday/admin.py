from django.contrib import admin

from holiday.models import Artist, Album, Classic, Song


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Artist, ArtistAdmin)


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'has_artwork')
    prepopulated_fields = {
        'slug': ('title',),
    }

    def has_artwork(self, obj):
        return bool(obj.artwork)
    has_artwork.boolean = True

admin.site.register(Album, AlbumAdmin)


class ClassicAdmin(admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Classic, ClassicAdmin)


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'track', 'album_name', 'rating', 'added')
    fields = ('title', 'artist', 'album', 'track', 'rating', 'added', 'buy_link', 'price', 'embed')

    def album_name(self, obj):
        try:
            return obj.album.title
        except AttributeError:
            return

admin.site.register(Song, SongAdmin)
