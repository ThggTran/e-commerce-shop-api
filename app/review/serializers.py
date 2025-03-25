from rest_framework import serializers

from core.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']