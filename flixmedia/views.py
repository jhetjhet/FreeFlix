from django.shortcuts import render
from rest_framework import viewsets

from .models import (
    Genre,
)
from .serializers import (
    GenreSerializer,
)

class GenreView (viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    