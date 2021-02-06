from django.db import models
from uuid import uuid4

class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tmdb_id = models.IntegerField()

    class Meta:
        abstract = True

class Flix(models.Model):
    title = models.CharField(max_length=255)
    tmdb_release_date = models.DateField()
    flix_release_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Media(models.Model):
    genres = models.ManyToManyField('Genre')

    class Meta:
        abstract = True
        ordering = ['flix_release_date']

class Genre(ID):
    name = models.CharField(max_length=255)
    GENRE_FOR_CHOICES = [
        ('mv', 'movie'),
        ('tv', 'tv'),
    ]
    genre_for = models.CharField(
        max_length = 2,
        choices = GENRE_FOR_CHOICES,
    )

class Movie(ID, Flix, Media):
    pass

class TV(ID, Flix, Media):
    pass

class Season(ID, Flix):
    tv = models.ForeignKey("TV", on_delete=models.CASCADE, related_name="seasons")
    season_number = models.IntegerField()

    class Meta:
        ordering = ['season_number']

class Episode(ID, Flix):
    season = models.ForeignKey("Season", on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.IntegerField()

    class Meta:
        ordering = ['episode_number']