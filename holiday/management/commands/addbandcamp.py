import json
from optparse import make_option
import sys

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.utils.text import slugify
import requests

from holiday.models import Song, Album, Artist


def all_input():
    while True:
        try:
            yield input('> ')
        except (EOFError, KeyboardInterrupt):
            return


class Command(NoArgsCommand):

    help = "Import a bandcamp album pasted to stdin"

    option_list = NoArgsCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Show successful checks too'),
    )

    def handle_noargs(self, **options):
        self.debug = options.get('debug', False)

        for line in all_input():
            try:
                cmd, data = line.split(' ', 1)
            except ValueError:
                cmd, data = line, None

            if cmd == 'bandcamp':
                self.bandcamp_url = data.strip()
                self.ratings = dict()
                self.is_various = False
            elif cmd == 'rate':
                track, rating = data.strip().split(' ', 1)
                track = int(track)
                rating = int(rating)
                self.ratings[track] = rating
            elif cmd == 'v/a':
                self.is_various = True
            elif cmd == 'done':
                self.save_album()

        print('')

    def album_data_for_url(self, url):
        resp = requests.get(url)
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('text/html')
        html = resp.text

        content_lines = list()
        capturing = False
        for line in html.split('\n'):
            if capturing:
                if line == '};':
                    capturing = False
                else:
                    content_lines.append(line.strip())
            elif line == 'var EmbedData = {':
                capturing = True
            elif line == 'var TralbumData = {':
                capturing = True

        album_data = dict()
        for line in content_lines:
            if line.startswith('//'):
                continue
            field, json_text = line.split(':', 1)
            field = field.strip()
            json_text = json_text.rstrip().rstrip(',')

            try:
                json_data = json.loads(json_text)
            except ValueError:
                print("Error evaluating json text for field", field, ", skipping")
            else:
                album_data[field] = json_data

        return album_data

    def save_album(self):
        album_data = self.album_data_for_url(self.bandcamp_url)

        if self.debug:
            self.stdout.write('Found Bandcamp album #{} for url {}'.format(
                album_data['id'], self.bandcamp_url))

        # Do we already have that album?
        try:
            album = Album.objects.get(buy_link=self.bandcamp_url)
            if self.debug:
                self.stdout.write('Loaded existing album {} for it'.format(album))
        except Album.DoesNotExist:
            album = Album(
                title=album_data['album_title'],
                slug=slugify(album_data['album_title'])[:50],
                buy_link=self.bandcamp_url,
            )
            if not self.is_various:
                artist_name = album_data['artist']
                artist, created = Artist.objects.get_or_create(slug=slugify(artist_name),
                    defaults={'name': artist_name})
                album.artist = artist

            album.save()

            if self.debug:
                self.stdout.write('Created new album {} for it'.format(album))

        album_tracks = dict()
        for track_data in album_data['trackinfo']:
            track_num = track_data['track_num']
            album_tracks[track_num] = track_data

        if self.debug:
            self.stdout.write('Album has tracks {}'.format(sorted(list(album_tracks.keys()))))
            self.stdout.write('Given tracks {} have ratings'.format(sorted(list(self.ratings.keys()))))

        # Add all the songs we have ratings for.
        songs = list()
        for track_num, rating in self.ratings.items():
            track_data = album_tracks[track_num]
            if self.is_various:
                artist_name, track_name = track_data['title'].split(' - ', 1)
            else:
                track_name = track_data['title']
                artist_name = None
            song_data = (track_num, track_name, artist_name, rating, None)
            songs.append(song_data)

        album.add_songs(songs)
        if self.debug:
            self.stdout.write('Added {} songs to {}'.format(len(songs), album))

        for track_num in self.ratings.keys():
            track_data = album_tracks[track_num]
            song = album.song_set.get(track=track_num)
            song.embed = """<iframe style="border: 0; width: 100%; height: 120px;" src="https://bandcamp.com/EmbeddedPlayer/album={album_id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=small/track={track_id}/transparent=true/" seamless><a href="{bandcamp_url}">{album_name} by {artist_name}</a></iframe>""".format(
                track_id=track_data['id'],
                album_id=album_data['id'],
                album_name=album.title,
                artist_name=song.artist.name,
                bandcamp_url=self.bandcamp_url,
            )
            song.save()
        if self.debug:
            self.stdout.write('Added embeds to {} songs. Yay!'.format(len(self.ratings)))
