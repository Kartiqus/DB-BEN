from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Wishlist

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ( 'rating', 'comment', 'created_at')
    can_delete = False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'is_featured', 'average_rating')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('average_rating', 'review_count')
    list_editable = ('price', 'stock', 'is_active', 'is_featured')
    inlines = [ProductImageInline, ReviewInline]
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Prix et stock', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Images', {
            'fields': ('thumbnail', 'image')
        }),
        ('Détails du produit', {
            'fields': ('ingredients', 'usage_instructions', 'weight')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistiques', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        })
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'comment')
    readonly_fields = ('created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ( 'product_count', 'created_at')
    filter_horizontal = ('products',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Nombre de produits'