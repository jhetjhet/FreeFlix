from django.core.management.base import BaseCommand, CommandError
from flixmedia.models import Movie
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
        parser.add_argument('-p', '--path', required=False, type=str, help='Path to video, left empty to use UI file picker')
        parser.add_argument('-o', '--override', action='store_true', help='Delete old video if present.')
        parser.add_argument('-m', '--move', action='store_true', help='Save and move video.')

    def handle(self, *args, **options):
        id = options['id']
        path = options['path']
        override = options['override']
        move = options['move']

        if not UUID4_REGEX.match(id):
            raise CommandError(f"'{id}' is not a valid uuid.")

        try:
            movie = Movie.objects.get(pk=id)
        except Movie.DoesNotExist:
            raise CommandError(f"Movie with id '{id}' does not exists")

        if not override and movie.video:
            raise CommandError(f"{movie.title} movie video is not null.")

        if not path:
            Tk().withdraw()
            path = askopenfile()
            if not path:
                return
            path = path.name
        elif path and not os.path.exists(path):
            raise CommandError(f"File {path} does not exists.")

        movie.link_local_video(path, move=move)

        self.stdout.write(self.style.SUCCESS(f"{movie.title} movie video {movie.video.name} with size: {movie.video.size}"))
        
            
        