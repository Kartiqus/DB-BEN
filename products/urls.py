from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
    path('wishlist/add/<int:product_id>/', views.WishlistViewSet.as_view({'post': 'add'})),
    path('wishlist/remove/<int:product_id>/', views.WishlistViewSet.as_view({'delete': 'remove'})),
]