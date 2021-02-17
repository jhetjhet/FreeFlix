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

class Video(models.Model):
    save_to = None
    video = models.FileField(null=True, default=None)

    def link_local_video(self, vid_path):
        _, filename = os.path.split(vid_path)
        vid_name = filename if not self.save_to else self.save_to(filename)
        vid_path_root = os.path.join(settings.MEDIA_ROOT, vid_name)
        Path(os.path.split(vid_path_root)[0]).mkdir(parents=True, exist_ok=True)
        os.rename(vid_path, vid_path_root)
        self.video.name = vid_name
        self.save()

    class Meta:
        abstract = True

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
    _, ext = os.path.splitext(filename)
    title = INVALID_FILE_CHARS.sub(' ', instance.title)
    return f"movie/{title} {instance.tmdb_id}/{title}{ext}"
class Movie(Media, Video):
    save_to = movie_file_path
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

def episode_file_path(instance, filename):
    tv = instance.season.tv
    tv_title = f"{tv.title} {tv.tmdb_id}"
    tv_title = INVALID_FILE_CHARS.sub(' ', tv_title)
    season_folder = f'season {instance.season.season_number}'
    _, ext = os.path.splitext(filename)
    episode_folder = f"episode {instance.episode_number}"
    episode_title = "{0}.S{1}E{2}{3}".format(
        tv.title, 
        str(instance.season.season_number).rjust(2, '0'),
        str(instance.episode_number).rjust(2, '0'),
        ext
    )
    episode_title = INVALID_FILE_CHARS.sub(' ', episode_title)
    return f"tv/{tv_title}/{season_folder}/{episode_folder}/{episode_title}"
class Episode(Flix, Video):
    save_to = episode_file_path
    ratings = models.ManyToManyField(Rate, related_name='episode_ratings')
    season = models.ForeignKey("Season", on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.IntegerField()

    class Meta:
        ordering = ['episode_number']
        constraints = [
            models.UniqueConstraint(fields=['season', 'episode_number'], name='unique_episode_number_per_season'),
        ]