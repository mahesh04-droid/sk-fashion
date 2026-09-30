import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk_fashion.settings')
django.setup()

from store.models import Category, Product, ProductVariant, StoreBanner, CustomerReview, Coupon

def populate():
    print("Clearing old sample data...")
    ProductVariant.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    StoreBanner.objects.all().delete()
    CustomerReview.objects.all().delete()

    print("Creating Menswear Categories...")
    cat_formal = Category.objects.create(
        name='Formal Shirts',
        description='Crisp cotton formal shirts designed for executive boardroom elegance and comfort.',
        icon='shirt',
        order=1
    )
    cat_casual = Category.objects.create(
        name='Casual Shirts',
        description='Breathable linen, printed cuban collars, and everyday casual button-downs.',
        icon='shirt',
        order=2
    )
    cat_denim = Category.objects.create(
        name='Denim & Jeans',
        description='Heavy-duty premium stretch denim in dark indigo, mid-blue, and clean black washes.',
        icon='scissors',
        order=3
    )
    cat_tshirts = Category.objects.create(
        name='Polo & T-Shirts',
        description='Bio-washed combed cotton t-shirts and luxury textured pique polo shirts.',
        icon='shirt',
        order=4
    )
    cat_trousers = Category.objects.create(
        name='Trousers & Chinos',
        description='Slim-tailored stretch chinos and formal wrinkle-free trousers for daily wear.',
        icon='user-tie',
        order=5
    )
    cat_ethnic = Category.objects.create(
        name='Kurta & Festive Wear',
        description='Designer kurtas, festive sets, and wedding wear crafted for celebratory occasions.',
        icon='star',
        order=6
    )

    print("Creating Menswear Products & Sizes...")
    products_data = [
        # Formal Shirts
        {
            'name': 'Giza Cotton Royal Oxford Formal Shirt - Sky Blue',
            'category': cat_formal,
            'description': 'Crafted from 100% long-staple Egyptian Giza cotton. Features a semi-spread collar, single cuff, and pearlized buttons. Wrinkle-resistant finish for all-day sharpness.',
            'fabric': '100% Giza Cotton (Double Ply)',
            'fit': 'Slim Fit',
            'color': 'Sky Blue',
            'price': 1699.00,
            'discount_price': 999.00,
            'image_url': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80',
            'image_2_url': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        },
        {
            'name': 'Executive Pristine White Herringbone Formal Shirt',
            'category': cat_formal,
            'description': 'The quintessential white shirt every gentleman needs. Textured herringbone weave with silky hand-feel and non-iron ease.',
            'fabric': '100% Combed Cotton',
            'fit': 'Regular Fit',
            'color': 'Pristine White',
            'price': 1599.00,
            'discount_price': 899.00,
            'image_url': 'https://images.unsplash.com/photo-1620012253295-c15c429f66bf?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        },
        {
            'name': 'Micro Windowpane Check Business Formal Shirt',
            'category': cat_formal,
            'description': 'Subtle navy micro check on white canvas. Pairs impeccably with grey or navy trousers for client meetings.',
            'fabric': 'Cotton Satin Blend',
            'fit': 'Slim Fit',
            'color': 'Navy / White',
            'price': 1499.00,
            'discount_price': 849.00,
            'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80',
            'is_featured': False,
            'is_bestseller': False,
            'sizes': ['M', 'L', 'XL'],
        },

        # Casual Shirts
        {
            'name': 'Pure European Linen Relaxed Casual Shirt - Olive',
            'category': cat_casual,
            'description': 'Airy, pre-washed 100% pure linen designed for effortless elegance. Naturally thermo-regulating for year-round comfort.',
            'fabric': '100% Pure Washed Linen',
            'fit': 'Relaxed Fit',
            'color': 'Olive Green',
            'price': 1899.00,
            'discount_price': 1199.00,
            'image_url': 'https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['M', 'L', 'XL', 'XXL'],
        },
        {
            'name': 'Vintage Buffalo Plaid Flannel Casual Shirt',
            'category': cat_casual,
            'description': 'Heavyweight brushed twill flannel shirt with dual chest pockets. Rugged construction with reinforced seams.',
            'fabric': '100% Brushed Cotton Flannel',
            'fit': 'Regular Fit',
            'color': 'Crimson & Navy',
            'price': 1699.00,
            'discount_price': 949.00,
            'image_url': 'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': False,
            'sizes': ['S', 'M', 'L', 'XL'],
        },
        {
            'name': 'Camp Collar Resort Printed Casual Shirt',
            'category': cat_casual,
            'description': 'Trendy resort-inspired botanical print with a retro cuban collar. Ultra-soft rayon fabric with fluid drape.',
            'fabric': 'Soft Rayon Twill',
            'fit': 'Relaxed Fit',
            'color': 'Black Tropical',
            'price': 1299.00,
            'discount_price': 749.00,
            'image_url': 'https://images.unsplash.com/photo-1589310243389-96a5483213a8?auto=format&fit=crop&w=800&q=80',
            'is_featured': False,
            'is_bestseller': True,
            'sizes': ['M', 'L', 'XL'],
        },

        # Denim & Jeans
        {
            'name': 'Deep Indigo Power-Stretch Slim Fit Jeans',
            'category': cat_denim,
            'description': '12.5 oz premium denim infused with 3% spandex for 360-degree flexibility. Retains shape after repeated washings without bagging at the knees.',
            'fabric': '97% Cotton, 3% Spandex Denim',
            'fit': 'Slim Fit',
            'color': 'Deep Indigo',
            'price': 2299.00,
            'discount_price': 1399.00,
            'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['28', '30', '32', '34', '36', '38'],
        },
        {
            'name': 'Midnight Jet Black Fade-Resistant Denim Jeans',
            'category': cat_denim,
            'description': 'Stay-black technology prevents fading up to 40 washes. Clean aesthetic suitable for both Friday casuals and party nights.',
            'fabric': 'Cotton Rich Stretch Denim',
            'fit': 'Slim Fit',
            'color': 'Jet Black',
            'price': 2199.00,
            'discount_price': 1299.00,
            'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['30', '32', '34', '36'],
        },

        # Trousers & Chinos
        {
            'name': 'Smart Flex 4-Way Stretch Chino Trousers - Khaki',
            'category': cat_trousers,
            'description': 'Versatile chinos engineered with an internal flexible waistband for maximum all-day comfort. Tailored flat-front design.',
            'fabric': 'Cotton Elastane Twill',
            'fit': 'Tailored Fit',
            'color': 'Classic Khaki',
            'price': 1799.00,
            'discount_price': 1099.00,
            'image_url': 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=800&q=80',
            'is_featured': False,
            'is_bestseller': True,
            'sizes': ['30', '32', '34', '36'],
        },
        {
            'name': 'Wrinkle-Free Formal Wool-Touch Trousers - Charcoal',
            'category': cat_trousers,
            'description': 'Crisp crease, sharp silhouette, and breathable poly-viscose blend. Ideal companion to formal blazers and shoes.',
            'fabric': 'Poly-Viscose Wool Blend',
            'fit': 'Regular Fit',
            'color': 'Charcoal Grey',
            'price': 1699.00,
            'discount_price': 999.00,
            'image_url': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': False,
            'sizes': ['30', '32', '34', '36', '38'],
        },

        # Kurta & Ethnic
        {
            'name': 'Lucknowi Chikankari Embroidered Festive Kurta - Wine Red',
            'category': cat_ethnic,
            'description': 'Intricate tone-on-tone embroidery across the chest and mandarin collar. Perfect for Diwali, Eid, Ganesh Utsav, and wedding receptions.',
            'fabric': 'Cotton Silk Blend',
            'fit': 'Regular Fit',
            'color': 'Wine Red',
            'price': 2499.00,
            'discount_price': 1499.00,
            'image_url': 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?auto=format&fit=crop&w=800&q=80',
            'is_featured': True,
            'is_bestseller': True,
            'sizes': ['M', 'L', 'XL', 'XXL'],
        },
        {
            'name': 'Minimalist Pure Cotton Pathani Kurta Set - Navy',
            'category': cat_ethnic,
            'description': 'Traditional royal Pathani cut featuring shoulder epaulettes and matching salwar pant. Breathable handloom cotton.',
            'fabric': '100% Handloom Cotton',
            'fit': 'Relaxed Fit',
            'color': 'Royal Navy',
            'price': 2299.00,
            'discount_price': 1349.00,
            'image_url': 'https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?auto=format&fit=crop&w=800&q=80',
            'is_featured': False,
            'is_bestseller': True,
            'sizes': ['M', 'L', 'XL', 'XXL'],
        },
    ]

    for p in products_data:
        sizes = p.pop('sizes')
        prod = Product.objects.create(**p)
        for s in sizes:
            ProductVariant.objects.create(product=prod, size=s, stock_quantity=12)

    print("Creating Customer Reviews from Ahilyanagar...")
    CustomerReview.objects.create(
        customer_name='Sachin Kulkarni',
        city='Sarjepura, Ahilyanagar',
        rating=5,
        comment='Best fitting shirts in Ahmednagar! I bought 3 formal shirts from their Delhi Gate store, fabric quality is better than top mall brands at half the price.',
        product_name='Giza Cotton Royal Oxford Shirt'
    )
    CustomerReview.objects.create(
        customer_name='Vaibhav Patil',
        city='Savedi, Ahilyanagar',
        rating=5,
        comment='Ordered on WhatsApp and got home delivery in 3 hours! Power-stretch jeans fit very well and fabric is super comfortable.',
        product_name='Deep Indigo Power-Stretch Jeans'
    )
    CustomerReview.objects.create(
        customer_name='Akshay Deshmukh',
        city='Kotla, Ahilyanagar',
        rating=5,
        comment='The Chikankari festive kurta was a hit at my brother’s engagement. Very authentic shop, friendly owner, highly recommended showroom.',
        product_name='Lucknowi Chikankari Festive Kurta'
    )

    print("Creating Promotional Coupons...")
    Coupon.objects.all().delete()
    Coupon.objects.create(
        code='SKF10',
        discount_percentage=10,
        min_order_amount=499,
        description='10% OFF on all menswear orders above ₹499'
    )
    Coupon.objects.create(
        code='WELCOME15',
        discount_percentage=15,
        min_order_amount=999,
        description='15% OFF for new customers on orders above ₹999'
    )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    populate()
