from html.parser import HTMLParser
from optparse import make_option
import re
import socket
from urllib.parse import urlsplit, parse_qsl

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
import requests

from holiday.models import Song, Album


class IframeSrcFinder(HTMLParser):

    iframe_src = None

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            for name, value in attrs:
                if name == 'src':
                    self.iframe_src = value


class Command(NoArgsCommand):

    help = "Checks all songs' embed codes for bad content"

    option_list = NoArgsCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Show successful checks too'),
        make_option('--skip',
            dest='skip',
            type=int,
            help='Skip to song with given ID'),
    )

    def handle_noargs(self, **options):
        self.debug = options.get('debug', False)

        checked = set()

        songs = Song.objects.exclude(embed='').order_by('id')
        if options.get('skip') is not None:
            songs = songs.filter(id__gt=options.get('skip'))
        for song in songs:
            parser = IframeSrcFinder()
            parser.feed(song.embed)
            iframe_src = parser.iframe_src

            if iframe_src is None:
                self.stderr.write("""Can't check non-iframe embed code for song #{} "{}" by {}\n""".format(
                    song.pk, song.title, song.artist.name))
                continue

            if iframe_src in checked:
                if self.debug:
                    self.stdout.write('Already checked iframe src for song #{} "{}" by {}\n'.format(
                        song.pk, song.title, song.artist.name))
                continue
            checked.add(iframe_src)

            # TODO: soundcloud urls don't 404 properly (Dear Santa – Jay Brannan)
            if 'youtube' in iframe_src:
                iframe_src = self.check_youtube(song, iframe_src)
            elif 'soundcloud' in iframe_src:
                iframe_src = self.check_soundcloud(song, iframe_src)

            try:
                r = requests.get(iframe_src, timeout=10)
            except socket.timeout:
                status_code = 503
            else:
                status_code = r.status_code

            if status_code != 200:
                self.stderr.write('Song #{} "{}" by {} has bad embed code iframe src {} (response code {})\n'.format(
                    song.pk, song.title, song.artist.name, iframe_src, status_code))
            elif self.debug:
                self.stdout.write('Song #{} "{}" by {} had a good embed code iframe src\n'.format(
                    song.pk, song.title, song.artist.name))

    def check_youtube(self, song, iframe_src):
        mo = re.search(r'(?:embed/)([\w-]{11})', iframe_src)
        if mo is None:
            raise ValueError("Could not determine YouTube video ID from apparent YouTube iframe url %s for song #{}".format(
                iframe_src, song.id))
        video_id = mo.group(1)

        data_url = 'http://gdata.youtube.com/feeds/api/videos/{}'.format(video_id)
        return data_url

    def check_soundcloud(self, song, iframe_src):
        # gimme the query args
        urlparts = urlsplit(iframe_src)
        quargs = dict(parse_qsl(urlparts.query))
        api_url = quargs['url']
        return '{}?client_id={}'.format(api_url, settings.SOUNDCLOUD_CLIENT_ID)
