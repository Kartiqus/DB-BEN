from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import OrderListView, OrderDetailView, CreateOrderView

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

from .views import OrderListView, OrderDetailView, CreateOrderView


urlpatterns = [
    path('', include(router.urls)),
    path('wishlist/add/<int:product_id>/', views.WishlistViewSet.as_view({'post': 'add'})),
    path('wishlist/remove/<int:product_id>/', views.WishlistViewSet.as_view({'delete': 'remove'})),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
