from django.contrib import admin

from holiday.models import Artist, Album, Song


admin.site.register(Artist)


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist')

admin.site.register(Album, AlbumAdmin)


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'rating', 'added')

admin.site.register(Song, SongAdmin)
