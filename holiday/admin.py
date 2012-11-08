from django.contrib import admin

from holiday.models import Artist, Album, Classic, Song


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


class ClassicAdmin(admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Classic, ClassicAdmin)


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'track', 'album_name', 'rating', 'added')

    def album_name(self, obj):
        try:
            return obj.album.title
        except AttributeError:
            return

admin.site.register(Song, SongAdmin)
