from django.contrib import admin
from .models import Category, Product, ProductVariant, StoreBanner, Order, OrderItem, CustomerReview, Coupon, CustomerProfile


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3
    fields = ('size', 'stock_quantity')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'min_order_amount', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('code', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'fit', 'fabric', 'is_available', 'is_featured', 'is_bestseller', 'is_new_arrival')
    list_filter = ('category', 'fit', 'is_available', 'is_featured', 'is_bestseller', 'is_new_arrival')
    list_editable = ('price', 'discount_price', 'is_available', 'is_featured', 'is_bestseller', 'is_new_arrival')
    search_fields = ('name', 'sku', 'description', 'fabric')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'sku', 'description')
        }),
        ('Garment Details', {
            'fields': ('fabric', 'fit', 'color')
        }),
        ('Pricing & Offers (INR)', {
            'fields': ('price', 'discount_price')
        }),
        ('Photography & Visuals', {
            'fields': ('image', 'image_url', 'image_2_url', 'image_3_url')
        }),
        ('Display & Inventory Flags', {
            'fields': ('is_available', 'is_featured', 'is_bestseller', 'is_new_arrival')
        }),
        ('Ratings & Social Proof', {
            'fields': ('rating', 'reviews_count')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'size', 'quantity', 'price', 'total_price')
    can_delete = False


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state', 'pincode', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__email', 'phone', 'city', 'pincode')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'customer_name', 'customer_phone', 'delivery_type', 'payment_method', 'payment_status', 'order_status', 'total_amount', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'delivery_type', 'created_at')
    list_editable = ('order_status', 'payment_status')
    search_fields = ('order_id', 'customer_name', 'customer_phone', 'city', 'pincode', 'razorpay_payment_id', 'upi_transaction_id')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'total_amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Identification', {
            'fields': ('order_id', 'order_status', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('user', 'customer_name', 'customer_phone', 'customer_email')
        }),
        ('Delivery Information', {
            'fields': ('delivery_type', 'address_line', 'city', 'state', 'pincode')
        }),
        ('Payment & Financials', {
            'fields': ('payment_method', 'payment_status', 'subtotal', 'coupon_code', 'discount_amount', 'delivery_charge', 'total_amount')
        }),
        ('Payment Gateway Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'upi_transaction_id'),
            'classes': ('collapse',)
        }),
        ('Special Instructions', {
            'fields': ('notes',)
        }),
    )


@admin.register(StoreBanner)
class StoreBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge', 'button_text', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    fieldsets = (
        ('Banner Headlines & Content', {
            'fields': ('title', 'subtitle', 'badge', 'button_text', 'button_link')
        }),
        ('Hero Image (Upload or Web URL)', {
            'fields': ('image', 'image_url'),
            'description': 'Upload your shop photo, model image, or paste an image URL to replace the homepage hero photo.'
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product', 'rating', 'city', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    list_editable = ('is_approved', 'is_verified')
    search_fields = ('customer_name', 'headline', 'comment', 'product__name', 'city')

