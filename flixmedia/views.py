from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .models import (
    Genre,
    Movie,
    TV,
    Season,
    Episode,
)
from .serializers import (
    GenreSerializer,
    MovieSerializer,
    TVSerializer,
    SeasonSerializer,
    EpisodeSerializer,
)

class GenreView (viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

class MovieView (viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

class TvView (viewsets.ModelViewSet):
    serializer_class = TVSerializer
    queryset = TV.objects.all()

class SeasonView (viewsets.ModelViewSet):
    serializer_class = SeasonSerializer
    lookup_field = 'season_number'
    
    def get_queryset(self):
        return TV.objects.filter(pk=self.kwargs['tv_pk']).first().seasons.all()

    def perform_create(self, serializer):
        tv = get_object_or_404(TV, pk=self.kwargs['tv_pk'])
        serializer.save(tv=tv)

class EpisodeView (viewsets.ModelViewSet):
    serializer_class = EpisodeSerializer
    lookup_field = 'episode_number'

    def get_season(self):
        tv = get_object_or_404(TV, pk=self.kwargs['tv_pk'])
        return get_object_or_404(tv.seasons, season_number=self.kwargs['season_number_season_number'])

    def get_queryset(self):
        return self.get_season().episodes.all()
    
    def perform_create(self, serializer):
        season = self.get_season()
        serializer.save(season=season)
