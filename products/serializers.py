from rest_framework import serializers
from .models import Category, Product, ProductImage, Review, Wishlist

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