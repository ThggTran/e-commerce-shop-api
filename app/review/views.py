from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import Review, Product
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        serializer.save(user=self.request.user, product=product)

