from .models import (
    Genre,
    Movie,
    TV,
    Season,
    Episode,
)
from django.db.models import Avg
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
        model = None
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
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.tmdb_id = validated_data.get('tmdb_id', instance.tmdb_id)
        instance.release_date = validated_data.get('release_data', instance.release_date)
        instance.save()
        return instance

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
    average_ratings = serializers.SerializerMethodField()

    class Meta (MediaBaseSerializer.Meta):
        model = Movie
        fields = MediaBaseSerializer.Meta.fields + ('average_ratings', )

    def get_average_ratings(self, obj):
        return obj.ratings.aggregate(score_avg=(Avg('score'))).get('score_avg')

class EpisodeSerializer (serializers.ModelSerializer):
    season_number = serializers.SlugRelatedField(read_only=True, slug_field='season_number')

    def save(self, season=None, *args, **kwargs):
        # Manual validation for season and episode_number UniqueConstraints
        # in save method where season instance is available
        episode_number = self.validated_data.get('episode_number')
        season = season or self.instance.season
        if (not self.instance or (self.instance and self.instance.episode_number != self.validated_data.get('episode_number'))) and season.episodes.filter(episode_number=episode_number).exists():
            raise serializers.ValidationError({'UniqueConstraint':f'seaon {season.season_number} already have episode {episode_number}'})
        super().save(season=season, *args, **kwargs)

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

    def save(self, tv=None, *args, **kwargs):
        # Manual validation for tv and season_number UniqueConstraints
        # in save method where tv instance is available
        season_number = self.validated_data.get('season_number')
        tv = tv or self.instance.tv
        if (not self.instance or (self.instance and self.instance.season_number != self.validated_data.get('season_number'))) and tv.seasons.filter(season_number=season_number).exists():
            raise serializers.ValidationError({'UniqueConstraint': f"TV '{tv.title}' already have season {season_number}"})
        super().save(tv=tv, *args, **kwargs)

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
    average_ratings = serializers.SerializerMethodField()
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta (MediaBaseSerializer.Meta):
        model = TV
        fields = MediaBaseSerializer.Meta.fields + ('average_ratings', 'seasons',)
    
    def get_average_ratings(self, obj):
        return obj.seasons.aggregate(score_avg=Avg('episodes__ratings__score')).get('score_avg')