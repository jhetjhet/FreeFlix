from django.contrib import admin

from .models import (
    Genre,
    Movie,
    TV,
    Season,
    Episode,
)

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(TV)
admin.site.register(Season)
admin.site.register(Episode)
