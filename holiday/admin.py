from django.contrib import admin

from holiday.models import Artist, Album, Classic, Song


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {
        'slug': ('name',),
    }
    search_fields = ('name',)
    readonly_fields = ('num_songs',)

admin.site.register(Artist, ArtistAdmin)


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'has_artwork', 'has_songs')
    prepopulated_fields = {
        'slug': ('title',),
    }
    search_fields = ('title', 'artist__name')

    def has_artwork(self, obj):
        return bool(obj.artwork)
    has_artwork.boolean = True

    def has_songs(self, obj):
        return bool(obj.songs())
    has_songs.boolean = True

admin.site.register(Album, AlbumAdmin)


class ClassicAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {
        'slug': ('title',),
    }
    search_fields = ('title',)

admin.site.register(Classic, ClassicAdmin)


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'track', 'album_name', 'rating', 'added', 'is_classic', 'has_embed')
    list_editable = ('rating',)
    fields = ('title', 'classic', 'artist', 'album', 'track', 'rating', 'added', 'buy_link', 'price', 'embed')
    search_fields = ('title', 'artist__name', 'album__title', 'classic__title')
    list_filter = ('rating', 'added')

    def has_embed(self, obj):
        return bool(obj.embed)
    has_embed.boolean = True

    def is_classic(self, obj):
        return bool(obj.classic)
    is_classic.boolean = True

    def album_name(self, obj):
        try:
            return obj.album.title
        except AttributeError:
            return

admin.site.register(Song, SongAdmin)
