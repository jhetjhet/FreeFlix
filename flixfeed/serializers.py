from rest_framework import serializers
from .models import Rate

class RateSerializer (serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rate
        fields = (
            'id',
            'user',
            'score',
            'date_rated',
        )