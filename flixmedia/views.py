from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)

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

from flixfeed.models import Rate
from flixfeed.serializers import RateSerializer

from rest_framework.response import Response

UUID4_REGEX = lookup_value_regex = r'(?i)[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}'

class GenreView (viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_value_regex = UUID4_REGEX

class ModelRatingActionViewSet (viewsets.ModelViewSet):
    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def rate(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            return get_object_or_404(Rate, user=request.user)
        
        elif request.method == 'DELETE':
            get_object_or_404(Rate, user=request.user).delete()
            return Response(status=HTTP_200_OK)

        elif request.method in ['POST', 'PUT']:
            rating_serializer = RateSerializer(data={'score': request.data.get('score', None)})
            if not rating_serializer.is_valid():
                return Response(rating_serializer.errors, status=HTTP_400_BAD_REQUEST)
        
        return Response(status=HTTP_200_OK)
    
    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'rate':
            return RateSerializer
        return self.flix_serializer_class

class MovieView (ModelRatingActionViewSet):
    flix_serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    lookup_value_regex = UUID4_REGEX

class TvView (viewsets.ModelViewSet):
    serializer_class = TVSerializer
    queryset = TV.objects.all()
    lookup_value_regex = UUID4_REGEX

class SeasonView (viewsets.ModelViewSet):
    serializer_class = SeasonSerializer
    lookup_field = 'season_number'
    lookup_value_regex = r'\d+'
    
    def get_queryset(self):
        return TV.objects.filter(pk=self.kwargs['tv_pk']).first().seasons.all()

    def perform_create(self, serializer):
        tv = get_object_or_404(TV, pk=self.kwargs['tv_pk'])
        serializer.save(tv=tv)

class EpisodeView (ModelRatingActionViewSet):
    flix_serializer_class = EpisodeSerializer
    lookup_field = 'episode_number'
    lookup_value_regex = r'\d+'

    def get_season(self):
        tv = get_object_or_404(TV, pk=self.kwargs['tv_pk'])
        return get_object_or_404(tv.seasons, season_number=self.kwargs['season_number_season_number'])

    def get_queryset(self):
        return self.get_season().episodes.all()
    
    def perform_create(self, serializer):
        season = self.get_season()
        serializer.save(season=season)
