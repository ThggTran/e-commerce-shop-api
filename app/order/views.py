from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from core.models import Cart, CartItem, Order, OrderItem
from order import serializers

class OrderViewSet(viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['POST'], detail=False, url_path='checkout')
    def checkout(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.items.select_related('product')

        if not cart_items.exists():
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo Order mới
        order = Order.objects.create(user=user)

        order_items = []
        total_price = 0

        # Auto chuyển toàn bộ CartItem -> OrderItem
        for item in cart_items:
            order_item = OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            order_items.append(order_item)
            total_price += item.product.price * item.quantity

        OrderItem.objects.bulk_create(order_items)  # Tạo nhiều dòng 1 lần

        # Cập nhật tổng tiền cho Order
        order.total_price = total_price
        order.save()

        # Xóa giỏ hàng
        cart.items.all().delete()

        return Response({
            'message': 'Order created successfully.',
            'order_id': order.id,
            'total_price': total_price
        }, status=status.HTTP_201_CREATED)
    

    @action(methods=['GET'], detail=False, url_path='list')
    def list_orders(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

