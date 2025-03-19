from rest_framework import serializers

from core.models import Product, Tag, Category

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields =['id','name','price', 'tags','category','stock','brand','model','warranty']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, product):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            product.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        self._get_or_create_tags(tags, product)

        return product
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags',None)
        
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
    
class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description']


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id','image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required':True}}