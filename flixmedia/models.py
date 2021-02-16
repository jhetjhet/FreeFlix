from django.conf import settings
from django.db import models
from uuid import uuid4
from flixfeed.models import Rate
from pathlib import Path
import re
import os

INVALID_FILE_CHARS = re.compile(r'[\\/:*?"<>|\s]+')

class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tmdb_id = models.IntegerField(unique=True)

    class Meta:
        abstract = True

class Flix(ID):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['date_uploaded']
    
    def __str__(self):
        return self.title

class Media(Flix):
    genres = models.ManyToManyField('Genre')

    class Meta (Flix.Meta):
        abstract = True

class VideoManager(object):

    def link_local_video(self, vid_path):
        _, filename = os.path.split(vid_path)
        vid_name = filename if not self.upload_to else self.upload_to(self, filename)
        vid_path_root = os.path.join(settings.MEDIA_ROOT, vid_name)
        Path(os.path.split(vid_path_root)[0]).mkdir(parents=True, exist_ok=True)
        os.rename(vid_path, vid_path_root)
        self.video.name = vid_name
        self.save()

class Genre(ID):
    # uniqness of name & tmdb_id is handled in api's
    # but not programmatically so be carefull
    name = models.CharField(max_length=255, unique=False)
    tmdb_id = models.IntegerField(unique=False)
    GENRE_FOR_CHOICES = [
        ('mv', 'movie'),
        ('tv', 'tv'),
    ]
    genre_for = models.CharField(
        max_length = 2,
        choices = GENRE_FOR_CHOICES,
    )

def movie_file_path(instance, filename):
    filename, ext = os.path.splitext(filename)
    title = INVALID_FILE_CHARS.sub(' ', instance.title)
    return f'movie/{title} {instance.tmdb_id}/{title}{ext}'
class Movie(Media):
    video = models.FileField(upload_to=movie_file_path, default=None)
    ratings = models.ManyToManyField(Rate, related_name='movie_ratings')

class TV(Media):
    pass

class Season(Flix):
    tv = models.ForeignKey("TV", on_delete=models.CASCADE, related_name="seasons")
    season_number = models.IntegerField()

    class Meta:
        ordering = ['season_number']
        constraints = [
            models.UniqueConstraint(fields=['tv', 'season_number'], name='unique_season_number_per_tv'),
        ]

class Episode(Flix, VideoManager):
    # upload_to = 
    ratings = models.ManyToManyField(Rate, related_name='episode_ratings')
    season = models.ForeignKey("Season", on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.IntegerField()

    class Meta:
        ordering = ['episode_number']
        constraints = [
            models.UniqueConstraint(fields=['season', 'episode_number'], name='unique_episode_number_per_season'),
        ]