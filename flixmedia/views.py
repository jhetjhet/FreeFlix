from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
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

UUID4_REGEX = r'(?i)[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}'

class GenreView (viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_value_regex = UUID4_REGEX

class GenreActionView (object):

    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def genre(self, request, pk=None, *args, **kwargs):
        media = self.get_object()

        if request.method == 'GET':
            return Response(GenreSerializer(media.genres.all(), many=True).data, status=HTTP_200_OK)
        elif request.method == 'POST':
            genre_serializer = GenreSerializer(data=request.data)
            if not genre_serializer.is_valid():
                return Response(genre_serializer.errors, status=HTTP_400_BAD_REQUEST)
            genre_obj, created = Genre.objects.get_or_create(
                tmdb_id=genre_serializer.data['tmdb_id'],
                defaults=genre_serializer.data
            )
            media.genres.add(genre_obj)
            data = GenreSerializer(genre_obj).data
            data['created'] = created
            return Response(data, status=HTTP_200_OK)
        elif request.method =='DELETE':
            if request.query_params.get('id') == None:
                return Response(status=HTTP_400_BAD_REQUEST)
            try:
                get_object_or_404(media.genres, id=request.query_params.get('id')).delete()
            except Exception as e:
                return Response(e, status=HTTP_400_BAD_REQUEST)
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

class RatingActionView (object):
    @action(detail=True, methods=['get', 'post', 'put', 'delete'])
    def rate(self, request, pk=None, *args, **kwargs):
        media = self.get_object()

        if request.method == 'GET':
            rate = get_object_or_404(media.ratings, user=request.user)
            return Response(RateSerializer(rate).data, status=HTTP_200_OK)
        
        elif request.method == 'DELETE':
            get_object_or_404(media.ratings, user=request.user).delete()
            return Response(status=HTTP_200_OK)

        elif request.method in ['POST', 'PUT']:
            score = request.data.get('score', None)
            rating_serializer = RateSerializer(data={'score': score})
            if not rating_serializer.is_valid():
                return Response(rating_serializer.errors, status=HTTP_400_BAD_REQUEST)
            rating_obj, created = media.ratings.get_or_create(
                user=request.user, 
                defaults={
                    'user': request.user,
                    **rating_serializer.data
                })
            if not created and rating_obj.score != int(score):
                rating_obj.score = score
                rating_obj.save()
            return Response(RateSerializer(rating_obj).data, status=HTTP_200_OK)
        else:
            return Response(status=HTTP_405_METHOD_NOT_ALLOWED)

class MovieView (GenreActionView, RatingActionView, viewsets.ModelViewSet):
    default_serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    lookup_value_regex = UUID4_REGEX
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        'title',
        'release_date',
    ]
    ordering_fields = [
        'title',
        'release_date',
        'date_uploaded',
        'average_ratings',
    ]

    def filter_queryset(self, queryset, *args, **kwargs):
        if 'average_ratings' in self.request.query_params.get('ordering', []):
            queryset = queryset.annotate(average_ratings=Avg('ratings__score'))
        return super(MovieView, self).filter_queryset(queryset, *args, **kwargs)

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'rate':
            return RateSerializer
        elif hasattr(self, 'action') and self.action == 'genre':
            return GenreSerializer
        return self.default_serializer_class

class TvView (viewsets.ModelViewSet):
    default_serializer_class = TVSerializer
    queryset = TV.objects.all()
    lookup_value_regex = UUID4_REGEX
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        'title',
        'release_date',
    ]
    ordering_fields = [
        'title',
        'release_date',
        'date_uploaded',
        'average_ratings',
    ]

    def filter_queryset(self, queryset, *args, **kwargs):
        if 'average_ratings' in self.request.query_params.get('ordering', []):
            queryset = queryset.annotate(average_ratings=Avg('seasons__episodes__ratings__score'))
        return super(TvView, self).filter_queryset(queryset, *args, **kwargs)

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'genre':
            return GenreSerializer
        return self.default_serializer_class

class SeasonView (viewsets.ModelViewSet):
    serializer_class = SeasonSerializer
    lookup_field = 'season_number'
    lookup_value_regex = r'\d+'
    
    def get_queryset(self):
        return TV.objects.filter(pk=self.kwargs['tv_pk']).first().seasons.all()

    def perform_create(self, serializer):
        tv = get_object_or_404(TV, pk=self.kwargs['tv_pk'])
        serializer.save(tv=tv)

class EpisodeView (RatingActionView, viewsets.ModelViewSet):
    default_serializer_class = EpisodeSerializer
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

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'rate':
            return RateSerializer
        return self.default_serializer_class