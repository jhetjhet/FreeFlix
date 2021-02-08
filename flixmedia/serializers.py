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
        fields = (
            'id',
            'tmdb_id',
            'name',
            'genre_for'
        )

class MediaBaseSerializer (serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=False)
    
    class Meta:
        abstract = True
        fields = (
            'id',
            'tmdb_id',
            'title',
            'release_date',
            'date_uploaded',
            'genres',
        )

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        media = self.Meta.model.objects.create(**validated_data)
        for genre in genres:
            genre_obj, _ = Genre.objects.get_or_create(
                tmdb_id = genre.get('tmdb_id', ''),
                defaults = genre
            )
            media.genres.add(genre_obj)
        return media

    def to_internal_value(self, data):
        _data = data.copy()
        genres_data = _data.pop('genres', []) # empty genres data so that it skip duplicate validation in parent to_internal value
        _data = super(MediaBaseSerializer, self).to_internal_value(_data)
        for genre in genres_data:
            genre_serializer = GenreSerializer(data=genre)
            if not genre_serializer.is_valid():
                raise serializers.ValidationError(genre_serializer.errors)
        _data['genres'] = genres_data
        return _data

class MovieSerializer (MediaBaseSerializer):
    
    class Meta:
        model = Movie
        fields = MediaBaseSerializer.Meta.fields

class EpisodeSerializer (serializers.ModelSerializer):
    season_number = serializers.SlugRelatedField(read_only=True, slug_field='season_number')

    class Meta:
        model = Episode
        fields = (
            'id',
            'tmdb_id',
            'title',
            'release_date',
            'date_uploaded',
            'episode_number',
            'season_number',
        )

class SeasonSerializer (serializers.ModelSerializer):
    tv = serializers.PrimaryKeyRelatedField(read_only=True)
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = (
            'id',
            'tmdb_id',
            'title',
            'release_date',
            'date_uploaded',
            'season_number',
            'tv',
            'episodes',
        )

class TVSerializer (MediaBaseSerializer):
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = TV
        fields = MediaBaseSerializer.Meta.fields + ('seasons',)