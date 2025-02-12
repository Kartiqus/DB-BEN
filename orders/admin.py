from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'total_amount', 'created_at', 'email')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__email', 'shipping_address', 'tracking_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Informations client', {
            'fields': ('user', 'email', 'phone')
        }),
        ('Adresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Statut de la commande', {
            'fields': ('status', 'payment_status')
        }),
        ('Informations de livraison', {
            'fields': ('tracking_number', 'notes')
        }),
        ('Informations financières', {
            'fields': ('total_amount', 'discount_amount', 'shipping_cost', 'coupon')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'total_amount')
        return self.readonly_fields

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('price',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'minimum_amount', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    list_editable = ('is_active', 'discount_percent')
    fieldsets = (
        ('Informations du coupon', {
            'fields': ('code', 'description')
        }),
        ('Réduction', {
            'fields': ('discount_percent', 'minimum_amount')
        }),
        ('Validité', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('code',)
        return ()