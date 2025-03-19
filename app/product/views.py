from jsonschema import ValidationError
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from user.permissions import  IsCustomer, IsSellerOrAdmin

from core.models import Tag, Product, Category
from product import serializers




class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSellerOrAdmin]

    
    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return self.queryset.order_by('-id')

        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductSerializer
        if self.action == 'upload_image':
            return serializers.ProductImageSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise ValidationError("Authentication credentials were not provided.")

    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class TagViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSellerOrAdmin]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

class CategoryViewSet(viewsets.ModelViewSet):
    
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSellerOrAdmin]

    def get_queryset(self):
        return self.queryset.order_by('-name')
