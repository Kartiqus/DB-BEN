from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Review, Wishlist
from .serializers import (
    CategorySerializer, ProductSerializer, ReviewSerializer, WishlistSerializer
)

from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer

class OrderListView(generics.ListAPIView):
    """ Liste toutes les commandes """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetailView(generics.RetrieveAPIView):
    """ Affiche une commande spécifique """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CreateOrderView(generics.CreateAPIView):
    """ Crée une nouvelle commande """
    queryset = Order.objects.all()
    serializer_class = CreateOrderSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True)
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured', 'is_active']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['created_at', 'price', 'name', 'stock']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        in_stock = self.request.query_params.get('in_stock')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock:
            queryset = queryset.filter(stock__gt=0)

        return queryset

    @action(detail=False)
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def similar(self, request, slug=None):
        product = self.get_object()
        similar = Product.objects.filter(
            Q(category=product.category) | 
            Q(ingredients__icontains=product.ingredients)
        ).exclude(id=product.id)[:5]
        serializer = self.get_serializer(similar, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def low_stock(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        products = self.get_queryset().filter(stock__lte=10).order_by('stock')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, request, slug=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier si l'utilisateur a déjà laissé un avis
            if Review.objects.filter(product=product, user=request.user).exists():
                return Response(
                    {'error': 'Vous avez déjà laissé un avis pour ce produit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si l'utilisateur a acheté le produit
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()
            
            serializer.save(
                product=product,
                user=request.user,
                is_verified_purchase=has_purchased
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def by_slug(self, request, slug=None):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def get_object(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

    @action(detail=False, methods=['post'])
    def add(self, request, product_id=None):
        wishlist = self.get_object()
        product = get_object_or_404(Product, id=product_id, is_active=True)
        if product in wishlist.products.all():
            return Response(
                {'message': 'Ce produit est déjà dans votre liste de souhaits'},
                status=status.HTTP_400_BAD_REQUEST
            )
        wishlist.products.add(product)
        return Response({'message': 'Produit ajouté à la liste de souhaits'})

    @action(detail=False, methods=['delete'])
    def remove(self, request, product_id=None):
        wishlist = self.get_object()
        product = get_object_or_404(Product, id=product_id)
        wishlist.products.remove(product)
        return Response({'message': 'Produit retiré de la liste de souhaits'})
