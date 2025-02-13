from rest_framework import serializers
from .models import Category, Product, ProductImage, Review, Wishlist
from .models import Order, OrderItem, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="orderitem_set", many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'status', 'total_price', 'items', 'created_at']
        read_only_fields = ['status', 'total_price', 'created_at']

class CreateOrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_price = 0
        order_items = []
        
        for item in items_data:
            product_id = item.get('product')
            quantity = item.get('quantity', 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Produit avec ID {product_id} introuvable")

            price = product.price * quantity
            total_price += price

            order_items.append(OrderItem(order=order, product=product, quantity=quantity, price=price))

        OrderItem.objects.bulk_create(order_items)
        order.total_price = total_price
        order.save()

        return order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'slug', 'is_active', 'product_count']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'order']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['user', 'is_verified_purchase']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    additional_images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'stock',
            'thumbnail', 'image', 'additional_images', 'ingredients',
            'usage_instructions', 'weight', 'is_active', 'is_featured',
            'slug', 'discount_price', 'average_rating', 'review_count',
            'reviews', 'is_in_stock', 'created_at'
        ]

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'products', 'created_at']
