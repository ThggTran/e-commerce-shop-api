from rest_framework import serializers

from core.models import CartItem, Cart, Product

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id','product', 'quantity', 'added_at']
        read_only_fields = ['id','added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price']
        read_only_fields = ['id', 'created_at']
    
    def get_total_price(self, obj)-> float:
        return obj.get_total_price()


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class UpdateQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


