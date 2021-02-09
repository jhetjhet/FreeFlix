from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from django.urls import path, include

from .views import (
    GenreView,
    MovieView,
    TvView,
    SeasonView,
    EpisodeView,
)

# rest_framework_nested is use to make url path related
# ex. to acces episode
# /tv/<tv_pk>/season/<season_number>/episode/<episode_number>
router = nested_routers.DefaultRouter()
router.register(r'genre', GenreView, basename='genre')
router.register(r'movie', MovieView, basename='movie')
router.register(r'tv', TvView, basename='tv')

tv_season_router = nested_routers.NestedDefaultRouter(router, r'tv', lookup='tv')
tv_season_router.register(r'season', SeasonView, basename='season')
tv_season_episode_router = nested_routers.NestedDefaultRouter(tv_season_router, r'season', lookup='season_number')
tv_season_episode_router.register(r'episode', EpisodeView, basename='episode')

urlpatterns = (
    path('', include(router.urls)),
    path('', include(tv_season_router.urls)),
    path('', include(tv_season_episode_router.urls)),
)