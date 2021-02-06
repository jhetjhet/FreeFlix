from rest_framework.routers import DefaultRouter

from .views import (
    GenreView,
)

router = DefaultRouter()
router.register(r'genre', GenreView, basename='genre')

urlpatterns = router.urls