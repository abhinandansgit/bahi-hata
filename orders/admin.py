from django.contrib import admin
from .models import Cart, CartItem, ComboCartItem, Order, OrderItem, ComboOrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'final_amount', 'coupon_code_used',
                    'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('user__username', 'user__email', 'shipping_address', 'coupon_code_used')
    readonly_fields = ('created_at', 'updated_at', 'coupon_code_used', 'times_used_snapshot')
    list_editable = ('status',)
    ordering = ('-created_at',)

    def times_used_snapshot(self, obj):
        return obj.coupon.times_used if obj.coupon else '—'
    times_used_snapshot.short_description = 'Coupon Uses'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'price')
    search_fields = ('book__title', 'order__id')


@admin.register(ComboOrderItem)
class ComboOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'combo_name_snapshot', 'quantity', 'price')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)

    def total_price(self, obj):
        return f"₹{obj.total_price}"
    total_price.short_description = 'Subtotal'


class ComboCartItemInline(admin.TabularInline):
    model = ComboCartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_price', 'updated_at')
    inlines = [CartItemInline, ComboCartItemInline]
    readonly_fields = ('created_at', 'updated_at')

    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = 'Items'

    def total_price(self, obj):
        return f"₹{obj.total_price}"
    total_price.short_description = 'Total'
