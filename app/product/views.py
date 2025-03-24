from jsonschema import ValidationError
from rest_framework import viewsets, mixins, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from user.permissions import  IsCustomer, IsSellerOrAdmin

from core.models import Tag, Product, Category
from product import serializers

from product.paginations import ProductPagination

class ProductReviewViewSet(generics.ListAPIView):
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        product_name = self.kwargs.get('name')
        return self.queryset.filter(name=product_name)
    
    


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSellerOrAdmin]

    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'brand', 'model']

    
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
        serializer.save(user=self.request.user)
        
        
    # def perform_create(self, serializer):
    #     if self.request.user.role != ['admin','seller']:
    #         raise PermissionDenied("You do not have permission to create products.")
    #     serializer.save(user=self.request.user)

    # def perform_update(self, serializer):
    #     obj = self.get_object()
    #     if not self.request.user.role =='admin' and obj.user != self.request.user:
    #         raise PermissionDenied("You do not have permission to modify this product.")
    #     serializer.save()

    # def perform_destroy(self, instance):
    #     if not self.request.user.role =='admin' and instance.user != self.request.user:
    #         raise PermissionDenied("You do not have permission to delete this product.")
    #     instance.delete()

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
        if self.action in ['list', 'retrieve']:
            return self.queryset.order_by('-id')

        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSellerOrAdmin]

    def get_queryset(self):
        return self.queryset.filter().order_by('-name')
    
    def perform_create(self, serializer):
        if not self.request.user.role == 'admin':
            raise PermissionDenied("You do not have permission.")
        serializer.save()
    
    def perform_update(self, serializer):
        if not self.request.user.role =='admin':
            raise PermissionDenied("You do not have permission.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.role =='admin':
            raise PermissionDenied("You do not have permission.")
        instance.delete()
