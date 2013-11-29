from html.parser import HTMLParser
from optparse import make_option

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
    )

    def handle_noargs(self, **options):
        debug = options.get('debug', False)

        checked = set()

        for song in Song.objects.exclude(embed=''):
            parser = IframeSrcFinder()
            parser.feed(song.embed)
            iframe_src = parser.iframe_src

            if iframe_src is None:
                self.stderr.write("""Can't check non-iframe embed code for song #{} "{}" by {}\n""".format(
                    song.pk, song.title, song.artist.name))
                continue

            if iframe_src in checked:
                if debug:
                    self.stdout.write('Already checked iframe src for song #{} "{}" by {}\n'.format(
                        song.pk, song.title, song.artist.name))
                continue
            checked.add(iframe_src)

            try:
                r = requests.get(iframe_src, timeout=10)
            except socket.timeout:
                status_code = 503
            else:
                status_code = r.status_code

            if status_code != 200:
                self.stderr.write('Song #{} "{}" by {} has bad embed code iframe src {} (response code {})\n'.format(
                    song.pk, song.title, song.artist.name, iframe_src, status_code))
            elif debug:
                self.stdout.write('Song #{} "{}" by {} had a good embed code iframe src\n'.format(
                    song.pk, song.title, song.artist.name))
