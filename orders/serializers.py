from rest_framework import serializers
from .models import Coupon, Order, OrderItem
from products.serializers import ProductSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'description', 'discount_percent', 'minimum_amount', 
                 'valid_from', 'valid_to', 'is_active']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(read_only=True)
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'status_display', 'payment_status',
            'total_amount', 'shipping_address', 'billing_address', 'phone',
            'email', 'tracking_number', 'notes', 'coupon', 'discount_amount',
            'shipping_cost', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'payment_status']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField())
    coupon_code = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = [
            'shipping_address', 'billing_address', 'phone', 'email',
            'notes', 'items', 'coupon_code'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        coupon_code = validated_data.pop('coupon_code', None)
        
        order = Order.objects.create(
            user=self.context['request'].user,
            **validated_data
        )

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                order.coupon = coupon
                order.save()
            except Coupon.DoesNotExist:
                pass

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order