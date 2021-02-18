from django.core.management.base import BaseCommand, CommandError
from flixmedia.models import (
    TV,
    Season,
    Episode
)
from flixmedia.views import UUID4_REGEX
from tkinter import Tk
from tkinter.filedialog import askopenfile
import os
import re

UUID4_REGEX = re.compile(UUID4_REGEX)

class Command (BaseCommand):
    help = 'Link local video to Movie and Episode.'

    def add_arguments(self, parser):
        parser.add_argument('id')
        parser.add_argument('-s', '--season', type=int, required=True, help='Season number.')
        parser.add_argument('-e', '--episode', type=int, required=True, help='Episode number.')
        parser.add_argument('-p', '--path', type=str, help='Path to video, left empty to use UI file picker')
        parser.add_argument('-o', '--override', action='store_true', help='Delete old video if present.')
        parser.add_argument('-m', '--move', action='store_true', help='Save and move video.')

    def handle(self, *args, **options):
        id = options['id']
        season_number = options['season']
        episode_number = options['episode']
        path = options['path']
        override = options['override']
        move = options['move']

        if not UUID4_REGEX.match(id):
            raise CommandError(f"'{id}' is not a valid uuid.")

        try:
            tv = TV.objects.get(pk=id)
            season = tv.seasons.get(season_number=season_number)
            episode = season.episodes.get(episode_number=episode_number)
        except TV.DoesNotExist:
            raise CommandError(f"TV with id '{id}' does not exists")
        except Season.DoesNotExist:
            raise CommandError(f"{tv.title} tv dont have season {season_number}")
        except Episode.DoesNotExist:
            raise CommandError(f"{tv.title} tv season {season_number} dont have episode {episode_number}")

        if not override and episode.video:
            raise CommandError(f"{episode.title} episode video is not null.")

        if not path:
            Tk().withdraw()
            path = askopenfile()
            if not path:
                return
            path = path.name
        elif path and not os.path.exists(path):
            raise CommandError(f"File {path} does not exists.")

        episode.link_local_video(path, move=move)

        self.stdout.write(self.style.SUCCESS(f"{tv.title} tv season {season_number} episode {episode_number} video {episode.video.name} with size: {episode.video.size}"))
        