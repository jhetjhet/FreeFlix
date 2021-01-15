from django.db import models
from uuid import uuid4

class Flix(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=255)
    tmdb_release_date = models.DateField()
    flix_release_date = models.DateField()

class Media(models.Model):
    genres = None

    class Meta:
        abstract = True
        ordering = ['flix_release_date']

class Movie(Media):
    pass

class TV(Media):
    pass

class Season(Media):
    season_number = models.IntegerField()

class Episode(Media):
    pass