from django.shortcuts import get_object_or_404
from jsonschema import ValidationError
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from cart import serializers
from user.permissions import  IsCustomer, IsSellerOrAdmin

from core.models import Cart, CartItem, Product
from drf_spectacular.utils import extend_schema


class CartItemViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.none()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):
        if self.action == 'add_to_cart':
            return serializers.AddToCartSerializer
        if self.action == 'update_quantity':
            return serializers.UpdateQuantitySerializer

        return self.serializer_class


    @action(methods=['POST'], detail=False, url_path='add-to-cart')
    def add_to_cart(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']

        product = get_object_or_404(Product, id=product_id)
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

        return Response({'message': 'Product added to cart.'}, status=status.HTTP_200_OK)


    @action(methods=['GET'], detail=False, url_path='view-cart')
    def view_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)

        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=['PATCH'], detail=True, url_path='update-quantity')
    def update_quantity(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        quantity = serializer.validated_data['quantity']

        if quantity is None or int(quantity) < 1:
            return Response({'error': 'Quantity must be >= 1.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = int(quantity)
        cart_item.save()
        return Response({'message': 'Quantity updated successfully.'}, status=status.HTTP_200_OK)


    @action(methods=['DELETE'], detail=True, url_path='remove-item')
    def remove_item(self, request, pk=None):
        cart_item = get_object_or_404(CartItem, id=pk, cart__user=request.user)
        cart_item.delete()
        return Response({'message': 'Item removed from cart.'}, status=status.HTTP_204_NO_CONTENT)

