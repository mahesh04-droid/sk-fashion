import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='shirt', help_text='Icon keyword (e.g. shirt, scissors, sparkle)')
    image_url = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Display Order / Sequence',
        help_text='Menu sorting position (e.g. 1 = first, 2 = second). Lower numbers appear first on the website.'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    FIT_CHOICES = [
        ('Slim Fit', 'Slim Fit'),
        ('Regular Fit', 'Regular Fit'),
        ('Relaxed Fit', 'Relaxed Fit'),
        ('Tailored Fit', 'Tailored Fit'),
        ('Standard', 'Standard Fit'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField()
    fabric = models.CharField(max_length=100, default='100% Premium Cotton', help_text='e.g., 100% Giza Cotton, Denim with Elastane')
    fit = models.CharField(max_length=50, choices=FIT_CHOICES, default='Slim Fit')
    color = models.CharField(max_length=50, default='Classic')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Original MRP in INR')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Special Offer / Selling Price in INR')
    
    # Images (Local upload and remote/CDN fallback)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, help_text='Direct URL for product photography')
    image_2_url = models.CharField(max_length=500, blank=True)
    image_3_url = models.CharField(max_length=500, blank=True)

    # Status flags
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=True)

    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    reviews_count = models.PositiveIntegerField(default=18)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + str(uuid.uuid4())[:6]
        if not self.sku:
            self.sku = f'SKF-{slugify(self.name)[:4].upper()}-{str(uuid.uuid4())[:4].upper()}'
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.price > self.discount_price and self.price > 0:
            diff = self.price - self.discount_price
            return int((diff / self.price) * 100)
        return 0

    @property
    def main_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80'

    @property
    def star_distribution(self):
        approved = self.reviews.filter(is_approved=True)
        total = approved.count()
        if total == 0:
            return {
                5: {'count': int(self.reviews_count * 0.70), 'pct': 70},
                4: {'count': int(self.reviews_count * 0.20), 'pct': 20},
                3: {'count': int(self.reviews_count * 0.08), 'pct': 8},
                2: {'count': int(self.reviews_count * 0.02), 'pct': 2},
                1: {'count': 0, 'pct': 0},
            }
        dist = {}
        for star in [5, 4, 3, 2, 1]:
            cnt = approved.filter(rating=star).count()
            pct = int(round((cnt / total) * 100)) if total > 0 else 0
            dist[star] = {'count': cnt, 'pct': pct}
        return dist

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('S', 'S (38)'),
        ('M', 'M (40)'),
        ('L', 'L (42)'),
        ('XL', 'XL (44)'),
        ('XXL', 'XXL (46)'),
        ('28', '28 (Waist)'),
        ('30', '30 (Waist)'),
        ('32', '32 (Waist)'),
        ('34', '34 (Waist)'),
        ('36', '36 (Waist)'),
        ('38', '38 (Waist)'),
        ('Free Size', 'Free Size'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    stock_quantity = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - Size {self.size} ({self.stock_quantity} in stock)"


class StoreBanner(models.Model):
    title = models.CharField(max_length=200, default="Upgrade Your Look With Premium Menswear")
    subtitle = models.CharField(max_length=300, default="Explore high-grade formal shirts, casual linen, stretch denim, and festival kurtas. Visit our showroom at Delhi Gate, Sarjepura or order online.")
    badge = models.CharField(max_length=100, default="Ahilyanagar's Exclusive Menswear Hub")
    button_text = models.CharField(max_length=50, default='Explore Collection')
    button_link = models.CharField(max_length=200, default='/products/')
    image = models.ImageField(upload_to='banners/', blank=True, null=True, help_text='Upload a hero photo from your device')
    image_url = models.CharField(max_length=500, blank=True, help_text='Or enter an image web URL')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    @property
    def banner_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?auto=format&fit=crop&w=800&q=80'

    def __str__(self):
        return self.title



class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(default=10, help_text='Discount in percent (e.g. 10 for 10% off)')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500, help_text='Minimum cart subtotal to apply')
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=200, blank=True, help_text='Offer summary e.g. 10% OFF on all menswear')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% OFF"


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('HOME_DELIVERY', 'Express Home Delivery'),
        ('STORE_PICKUP', 'Store Pickup (Delhi Gate, Ahilyanagar Showroom)'),
        ('COUNTER_SALE', 'Showroom Walk-in Sale (Delhi Gate Counter)'),
    ]

    PAYMENT_CHOICES = [
        ('RAZORPAY', 'Razorpay Online (Cards / UPI / NetBanking / Wallets)'),
        ('UPI_QR', 'Scan & Pay (Instant UPI QR)'),
        ('IN_STORE_CASH', 'Showroom Cash Payment'),
        ('IN_STORE_UPI', 'Showroom Counter UPI (GPay / PhonePe QR Standee)'),
        ('IN_STORE_CARD', 'Showroom Card Swipe Machine'),
        ('UPI_ONLINE', 'UPI / Online Payment'),
        ('COD', 'Cash on Delivery (COD)'),
        ('WHATSAPP_ORDER', 'Confirmed via WhatsApp Chat'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('COMPLETED', 'Paid Successfully'),
        ('COD_VERIFIED', 'Cash on Delivery Verified'),
        ('FAILED', 'Payment Failed'),
    ]

    ORDER_STATUS_CHOICES = [
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Order Confirmed'),
        ('PACKED', 'Packed & Ready'),
        ('SHIPPED', 'Dispatched / In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('READY_FOR_PICKUP', 'Ready for Store Pickup'),
        ('DELIVERED', 'Delivered / Picked Up'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    
    delivery_type = models.CharField(max_length=30, choices=DELIVERY_CHOICES, default='HOME_DELIVERY')
    address_line = models.TextField(blank=True, help_text='House/Shop no, street, landmark')
    city = models.CharField(max_length=100, default='Ahilyanagar')
    state = models.CharField(max_length=100, default='Maharashtra')
    pincode = models.CharField(max_length=10, blank=True, default='414001')

    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='RAZORPAY')
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='PLACED')

    CALL_VERIFICATION_CHOICES = [
        ('PENDING', 'Pending Call'),
        ('VERIFIED', 'Call Verified & Confirmed'),
        ('UNREACHABLE', 'Unreachable / Not Answering'),
        ('FAKE', 'Fake / Invalid Order'),
    ]
    call_verification_status = models.CharField(
        max_length=20,
        choices=CALL_VERIFICATION_CHOICES,
        default='PENDING',
        help_text='Phone verification status before packing'
    )
    call_notes = models.CharField(max_length=255, blank=True, help_text='Staff call verification notes')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    # Online Payment fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    upi_transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text='UTR / UPI Ref Number')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"SKF-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer_name} (₹{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size})"


class CustomerReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20, blank=True, null=True, help_text='Used to verify purchase history')
    city = models.CharField(max_length=100, default='Ahilyanagar')
    rating = models.IntegerField(default=5, help_text='Rating 1 to 5')
    headline = models.CharField(max_length=150, blank=True, help_text='Short summary headline')
    comment = models.TextField()
    product_name = models.CharField(max_length=150, default='Menswear Collection')
    is_verified = models.BooleanField(default=True, help_text='Verified Buyer badge')
    is_approved = models.BooleanField(default=True, help_text='Approved for public display')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.customer_phone and self.product:
            from .models import OrderItem
            has_ordered = OrderItem.objects.filter(
                order__customer_phone__icontains=self.customer_phone.strip(),
                product=self.product
            ).exists()
            if has_ordered:
                self.is_verified = True

        super().save(*args, **kwargs)

        if self.product:
            approved = self.product.reviews.filter(is_approved=True)
            cnt = approved.count()
            if cnt > 0:
                avg = approved.aggregate(models.Avg('rating'))['rating__avg'] or 5.0
                self.product.rating = round(avg, 1)
                self.product.reviews_count = cnt
                self.product.save(update_fields=['rating', 'reviews_count'])

    def __str__(self):
        prod_title = self.product.name if self.product else self.product_name
        return f"{self.customer_name} ({self.rating}★) - {prod_title}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address_line = models.TextField(blank=True, help_text='House/flat, street, landmark')
    city = models.CharField(max_length=100, default='Ahilyanagar')
    state = models.CharField(max_length=100, default='Maharashtra')
    pincode = models.CharField(max_length=10, blank=True, default='414001')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.phone or 'No phone'})"


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.get_or_create(user=instance)

