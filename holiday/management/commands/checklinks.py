from optparse import make_option
import socket

from django.core.management.base import NoArgsCommand, CommandError
import requests

from holiday.models import Song, Album


class Command(NoArgsCommand):

    help = "Checks all songs' buy links for bad content"

    option_list = NoArgsCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Show successful checks too'),
    )

    def handle_noargs(self, **options):
        debug = options.get('debug', False)

        checked_links = set()

        def buyable():
            for song in Song.objects.exclude(buy_link='').order_by('id'):
                yield song
            for album in Album.objects.exclude(buy_link='').order_by('id'):
                yield album

        for obj in buyable():
            buy_link = obj.buy_link

            if buy_link in checked_links:
                if debug:
                    self.stdout.write('Already checked buy link for {} #{} "{}" by {}'.format(
                        type(obj).__name__, obj.pk, obj.title, 'v/a' if obj.artist is None else obj.artist.name))
                continue
            checked_links.add(buy_link)

            try:
                r = requests.get(buy_link, timeout=10)
            except socket.timeout:
                status_code = 503
            else:
                status_code = r.status_code

            if status_code != 200:
                self.stderr.write('{} #{} "{}" by {} has bad link {} (response code {})\n'.format(
                    type(obj).__name__, obj.pk, obj.title, 'v/a' if obj.artist is None else obj.artist.name, obj.buy_link, status_code))
            elif debug:
                self.stdout.write('{} #{} "{}" by {} had a good buy link\n'.format(
                    type(obj).__name__, obj.pk, obj.title, 'v/a' if obj.artist is None else obj.artist.name))
