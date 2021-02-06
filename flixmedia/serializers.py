from .models import (
    Genre,
    Movie,
    TV,
    Season,
    Episode,
)
from rest_framework import serializers

class GenreSerializer (serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'tmdb_id',
            'name',
            'genre_for'
        ]

# class MovieSerializer (serializers.ModelSerializer):
#     class Meta:
#         model = Movie
#         fields = [
#             ''
#         ]