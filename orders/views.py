from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum
from .models import Order, Coupon
from .serializers import OrderSerializer, OrderCreateSerializer, CouponSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status = request.data.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            return Response({'status': status})
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        return Response({'status': 'cancelled'})

    @action(detail=False)
    def dashboard_stats(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        recent_revenue = Order.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        )

        return Response({
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'total_revenue': total_revenue,
            'recent_revenue': recent_revenue,
            'orders_by_status': orders_by_status,
        })

class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer

    @action(detail=False, methods=['post'])
    def verify(self, request):
        code = request.data.get('code')
        try:
            coupon = Coupon.objects.get(
                code=code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
            return Response(self.get_serializer(coupon).data)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired coupon'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def apply(self, request):
        code = request.data.get('code')
        amount = request.data.get('amount')

        try:
            coupon = Coupon.objects.get(
                code=code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )

            if amount < coupon.minimum_amount:
                return Response(
                    {'error': 'Order amount does not meet minimum requirement'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            discount = (amount * coupon.discount_percent) / 100
            return Response({
                'discount': discount,
                'final_amount': amount - discount
            })

        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired coupon'},
                status=status.HTTP_404_NOT_FOUND
            )