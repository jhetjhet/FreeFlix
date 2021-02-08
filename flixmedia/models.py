from django.db import models
from uuid import uuid4

class ID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tmdb_id = models.IntegerField()

    class Meta:
        abstract = True

class Flix(ID):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['date_uploaded']

class Media(Flix):
    genres = models.ManyToManyField('Genre')

    class Meta (Flix.Meta):
        abstract = True

class Genre(ID):
    name = models.CharField(max_length=255, unique=True)
    GENRE_FOR_CHOICES = [
        ('mv', 'movie'),
        ('tv', 'tv'),
    ]
    genre_for = models.CharField(
        max_length = 2,
        choices = GENRE_FOR_CHOICES,
    )

class Movie(Media):

    class Meta (Media.Meta):
        constraints = [
            models.UniqueConstraint(fields=['id', 'genres'], name='movie_id_genre_unique_constraint'),
        ]

class TV(Media):
    
    class Meta (Media.Meta):
        constraints = [
            models.UniqueConstraint(fields=['id', 'genres'], name='tv_id_genre_unique_constraint'),
        ]

class Season(Flix):
    tv = models.ForeignKey("TV", on_delete=models.CASCADE, related_name="seasons")
    season_number = models.IntegerField(unique=True)

    class Meta:
        ordering = ['season_number']

class Episode(Flix):
    season = models.ForeignKey("Season", on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.IntegerField(unique=True)

    class Meta:
        ordering = ['episode_number']