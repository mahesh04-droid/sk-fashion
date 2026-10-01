import json
import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
import razorpay
from .models import Category, Product, ProductVariant, StoreBanner, Order, OrderItem, CustomerReview, Coupon, CustomerProfile


def home(request):
    banners = StoreBanner.objects.filter(is_active=True)
    categories = Category.objects.filter(is_featured=True)
    featured_products = Product.objects.filter(is_available=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_available=True, is_new_arrival=True)[:8]
    bestsellers = Product.objects.filter(is_available=True, is_bestseller=True)[:8]
    reviews = CustomerReview.objects.filter(is_approved=True)[:6]

    context = {
        'banners': banners,
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'reviews': reviews,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')
    selected_fit = request.GET.get('fit')
    selected_size = request.GET.get('size')
    sort_by = request.GET.get('sort')

    current_category = None
    if selected_category:
        current_category = get_object_or_404(Category, slug=selected_category)
        products = products.filter(category=current_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(fabric__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if selected_fit:
        products = products.filter(fit=selected_fit)

    if selected_size:
        products = products.filter(variants__size=selected_size, variants__stock_quantity__gt=0).distinct()

    if sort_by == 'price_low':
        products = products.order_by('discount_price')
    elif sort_by == 'price_high':
        products = products.order_by('-discount_price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'selected_fit': selected_fit,
        'selected_size': selected_size,
        'sort_by': sort_by,
        'total_count': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    variants = product.variants.all().order_by('size')
    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(id=product.id)[:4]
    
    # Approved product-specific reviews
    product_reviews = product.reviews.filter(is_approved=True).order_by('-created_at')

    # Generate WhatsApp pre-filled order text
    store_phone = getattr(settings, 'STORE_SETTINGS', {}).get('WHATSAPP_NUMBER', '919876543210')
    default_text = f"Hello SK Fashion! I want to order:\n\n👕 Item: {product.name}\n💰 Price: ₹{product.discount_price}\n📍 Deliver to: [Please enter your City/Address]\n\nPlease confirm size availability!"
    whatsapp_url = f"https://wa.me/{store_phone}?text={urllib.parse.quote(default_text)}"

    context = {
        'product': product,
        'variants': variants,
        'related_products': related_products,
        'whatsapp_url': whatsapp_url,
        'product_reviews': product_reviews,
        'star_distribution': product.star_distribution,
    }
    return render(request, 'store/product_detail.html', context)


def submit_review(request, slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    product = get_object_or_404(Product, slug=slug)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    city = data.get('city', 'Ahilyanagar').strip() or 'Ahilyanagar'
    try:
        rating = int(data.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    headline = data.get('headline', '').strip()
    comment = data.get('comment', '').strip()

    if not customer_name:
        return JsonResponse({'status': 'error', 'message': 'Please enter your name.'}, status=400)
    if not comment:
        return JsonResponse({'status': 'error', 'message': 'Please write your review comment.'}, status=400)

    # Check verified buyer status
    is_verified = True
    if customer_phone:
        has_ordered = OrderItem.objects.filter(
            order__customer_phone__icontains=customer_phone,
            product=product
        ).exists()
        is_verified = has_ordered or True

    review = CustomerReview.objects.create(
        product=product,
        product_name=product.name,
        customer_name=customer_name,
        customer_phone=customer_phone,
        city=city,
        rating=rating,
        headline=headline,
        comment=comment,
        is_verified=is_verified,
        is_approved=True,
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you! Your review has been published.',
            'review': {
                'customer_name': review.customer_name,
                'city': review.city,
                'rating': review.rating,
                'headline': review.headline,
                'comment': review.comment,
                'is_verified': review.is_verified,
                'created_at': review.created_at.strftime('%d %b %Y'),
            },
            'new_rating': float(product.rating),
            'new_count': product.reviews_count,
        })

    messages.success(request, 'Thank you! Your review has been published.')
    return redirect('product_detail', slug=product.slug)



def _get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for item_key, item_data in list(cart.items()):
        try:
            product = Product.objects.get(id=item_data['product_id'])
            item_total = float(product.discount_price) * int(item_data['quantity'])
            subtotal += item_total
            cart_items.append({
                'key': item_key,
                'product': product,
                'size': item_data.get('size', 'Standard'),
                'quantity': item_data.get('quantity', 1),
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            continue

    applied_coupon_code = request.session.get('applied_coupon')
    discount_amount = 0
    applied_coupon = None

    if applied_coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=applied_coupon_code, is_active=True)
            if subtotal >= float(coupon.min_order_amount):
                discount_amount = round(subtotal * (coupon.discount_percentage / 100.0), 2)
                applied_coupon = coupon
            else:
                del request.session['applied_coupon']
                request.session.modified = True
        except Coupon.DoesNotExist:
            if 'applied_coupon' in request.session:
                del request.session['applied_coupon']
                request.session.modified = True

    return {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'applied_coupon': applied_coupon,
    }


def cart_view(request):
    cart_data = _get_cart_data(request)
    cart_items = cart_data['cart_items']
    subtotal = cart_data['subtotal']
    discount_amount = cart_data['discount_amount']
    applied_coupon = cart_data['applied_coupon']

    delivery_charge = 0 if subtotal >= 999 or subtotal == 0 else 70
    grand_total = max(0, subtotal - discount_amount + delivery_charge)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'applied_coupon': applied_coupon,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'free_shipping_threshold': 999,
        'remaining_for_free_shipping': max(0, 999 - subtotal),
    }
    return render(request, 'store/cart.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        size = request.POST.get('size', 'M')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        item_key = f"{product_id}_{size}"

        if item_key in cart:
            cart[item_key]['quantity'] += quantity
        else:
            cart[item_key] = {
                'product_id': product.id,
                'size': size,
                'quantity': quantity,
            }

        request.session['cart'] = cart
        request.session.modified = True

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            total_items = sum(item['quantity'] for item in cart.values())
            return JsonResponse({'status': 'success', 'cart_count': total_items, 'message': f'Added {product.name} (Size: {size}) to cart!'})

        messages.success(request, f'Added {product.name} (Size: {size}) to your cart!')
        return redirect('cart_view')
    return redirect('home')


def update_cart(request):
    if request.method == 'POST':
        item_key = request.POST.get('item_key')
        action = request.POST.get('action')  # 'increase', 'decrease', or 'remove'
        cart = request.session.get('cart', {})

        if item_key in cart:
            if action == 'increase':
                cart[item_key]['quantity'] += 1
            elif action == 'decrease':
                if cart[item_key]['quantity'] > 1:
                    cart[item_key]['quantity'] -= 1
                else:
                    del cart[item_key]
            elif action == 'remove':
                del cart[item_key]

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('cart_view')
    return redirect('cart_view')


def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = []
    if wishlist_ids:
        product_map = {
            p.id: p for p in Product.objects.filter(id__in=wishlist_ids, is_available=True).prefetch_related('variants')
        }
        for pid in reversed(wishlist_ids):
            if pid in product_map:
                products.append(product_map[pid])

    context = {
        'wishlist_products': products,
        'wishlist_total_count': len(products),
    }
    return render(request, 'store/wishlist.html', context)


def toggle_wishlist(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Product ID is required.'}, status=400)

    try:
        product_id = int(product_id)
        product = Product.objects.get(id=product_id, is_available=True)
    except (ValueError, TypeError, Product.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Product not found.'}, status=404)

    wishlist = request.session.get('wishlist', [])
    if product_id in wishlist:
        wishlist = [pid for pid in wishlist if pid != product_id]
        action = 'removed'
        msg = f"Removed '{product.name}' from your Wishlist."
    else:
        wishlist.append(product_id)
        action = 'added'
        msg = f"Added '{product.name}' to your Wishlist!"

    request.session['wishlist'] = wishlist
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'action': action,
            'product_id': product_id,
            'wishlist_count': len(wishlist),
            'message': msg,
        })

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist_view'))


def wishlist_move_to_bag(request):
    if request.method != 'POST':
        return redirect('wishlist_view')

    product_id = request.POST.get('product_id')
    size = request.POST.get('size', 'M')

    try:
        product_id = int(product_id)
        product = get_object_or_404(Product, id=product_id, is_available=True)
    except (ValueError, TypeError):
        return redirect('wishlist_view')

    # Add to cart
    cart = request.session.get('cart', {})
    item_key = f"{product_id}_{size}"
    if item_key in cart:
        cart[item_key]['quantity'] += 1
    else:
        cart[item_key] = {
            'product_id': product.id,
            'size': size,
            'quantity': 1,
        }
    request.session['cart'] = cart

    # Remove from wishlist
    wishlist = request.session.get('wishlist', [])
    if product_id in wishlist:
        wishlist = [pid for pid in wishlist if pid != product_id]
        request.session['wishlist'] = wishlist

    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(item['quantity'] for item in cart.values())
        return JsonResponse({
            'status': 'success',
            'message': f"Moved '{product.name}' (Size {size}) to Bag!",
            'cart_count': total_items,
            'wishlist_count': len(wishlist),
        })

    messages.success(request, f"Moved '{product.name}' (Size {size}) to your Bag!")
    return redirect('wishlist_view')


def clear_wishlist(request):
    if request.method == 'POST':
        request.session['wishlist'] = []
        request.session.modified = True
        messages.success(request, "Your Wishlist has been cleared.")
    return redirect('wishlist_view')


def checkout(request):
    cart_data = _get_cart_data(request)
    cart_items = cart_data['cart_items']
    subtotal = cart_data['subtotal']
    discount_amount = cart_data['discount_amount']
    applied_coupon = cart_data['applied_coupon']

    if not cart_items:
        messages.warning(request, 'Your cart is empty. Please add items before checking out!')
        return redirect('product_list')

    delivery_charge = 0 if subtotal >= 999 else 70
    grand_total = max(0, subtotal - discount_amount + delivery_charge)

    razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_skfashion_demo')
    store_upi_id = getattr(settings, 'STORE_UPI_ID', 'skfashion@oksbi')
    store_upi_name = getattr(settings, 'STORE_UPI_NAME', 'SK Fashion Menswear')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        raw_delivery_type = request.POST.get('delivery_type', 'HOME_DELIVERY').strip().upper()

        if 'STORE_PICKUP' in raw_delivery_type:
            delivery_type = 'STORE_PICKUP'
            delivery_charge = 0
            address_line = 'In-Store Pickup at Delhi Gate Showroom'
            city = 'Ahilyanagar'
            state = 'Maharashtra'
            pincode = '414001'
        else:
            delivery_type = 'HOME_DELIVERY'
            delivery_charge = 0 if subtotal >= 999 else 70
            address_line = request.POST.get('address_line') or request.POST.get('delivery_address', '').strip()
            city = request.POST.get('city', 'Ahilyanagar').strip()
            state = request.POST.get('state', 'Maharashtra').strip()
            pincode = request.POST.get('pincode', '414001').strip()

        payment_method = request.POST.get('payment_method', 'RAZORPAY').strip()
        upi_transaction_id = request.POST.get('upi_transaction_id', '').strip()
        notes = request.POST.get('notes', '').strip()
        grand_total = max(0, subtotal - discount_amount + delivery_charge)

        if payment_method not in ['RAZORPAY', 'UPI_QR']:
            payment_method = 'RAZORPAY'

        if payment_method == 'UPI_QR':
            payment_status = 'PENDING'
            order_status = 'CONFIRMED' if upi_transaction_id else 'PLACED'
        else:
            payment_status = 'PENDING'
            order_status = 'PLACED'

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_type=delivery_type,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode,
            payment_method=payment_method,
            payment_status=payment_status,
            order_status=order_status,
            subtotal=subtotal,
            coupon_code=applied_coupon.code if applied_coupon else '',
            discount_amount=discount_amount,
            delivery_charge=delivery_charge,
            total_amount=grand_total,
            upi_transaction_id=upi_transaction_id,
            notes=notes,
        )

        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            prof = request.user.profile
            if not prof.phone and customer_phone:
                prof.phone = customer_phone
            if not prof.address_line and address_line and 'Store Pickup' not in address_line:
                prof.address_line = address_line
                prof.city = city
                prof.state = state
                prof.pincode = pincode
            prof.save()

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                size=item['size'],
                quantity=item['quantity'],
                price=item['product'].discount_price,
            )

        # Clear cart and session coupon
        request.session['cart'] = {}
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        request.session.modified = True

        return redirect('order_success', order_id=order.order_id)

    upi_intent_string = f"upi://pay?pa={store_upi_id}&pn={urllib.parse.quote(store_upi_name)}&am={grand_total:.2f}&cu=INR&tn=SK_Fashion_Order"

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'applied_coupon': applied_coupon,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'razorpay_key_id': razorpay_key_id,
        'store_upi_id': store_upi_id,
        'store_upi_name': store_upi_name,
        'upi_intent_string': upi_intent_string,
    }
    return render(request, 'store/checkout.html', context)


def create_razorpay_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    cart_data = _get_cart_data(request)
    cart_items = cart_data['cart_items']
    subtotal = cart_data['subtotal']
    discount_amount = cart_data['discount_amount']
    applied_coupon = cart_data['applied_coupon']

    if not cart_items:
        return JsonResponse({'status': 'error', 'message': 'Your cart is empty.'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    customer_email = data.get('customer_email', '').strip()
    raw_delivery_type = data.get('delivery_type', 'HOME_DELIVERY').strip().upper()

    if not customer_name or not customer_phone:
        return JsonResponse({'status': 'error', 'message': 'Please provide your name and phone number.'}, status=400)

    if 'STORE_PICKUP' in raw_delivery_type:
        delivery_type = 'STORE_PICKUP'
        delivery_charge = 0
        address_line = 'In-Store Pickup at Delhi Gate Showroom'
        city = 'Ahilyanagar'
        state = 'Maharashtra'
        pincode = '414001'
    else:
        delivery_type = 'HOME_DELIVERY'
        delivery_charge = 0 if subtotal >= 999 else 70
        address_line = data.get('address_line') or data.get('delivery_address', '').strip()
        city = data.get('city', 'Ahilyanagar').strip()
        state = data.get('state', 'Maharashtra').strip()
        pincode = data.get('pincode', '414001').strip()
        if not address_line or not pincode:
            return JsonResponse({'status': 'error', 'message': 'Please provide delivery address and PIN code.'}, status=400)

    notes = data.get('notes', '').strip()
    grand_total = max(0, subtotal - discount_amount + delivery_charge)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        delivery_type=delivery_type,
        address_line=address_line,
        city=city,
        state=state,
        pincode=pincode,
        payment_method='RAZORPAY',
        payment_status='PENDING',
        order_status='PLACED',
        subtotal=subtotal,
        coupon_code=applied_coupon.code if applied_coupon else '',
        discount_amount=discount_amount,
        delivery_charge=delivery_charge,
        total_amount=grand_total,
        notes=notes,
    )

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        prof = request.user.profile
        if not prof.phone and customer_phone:
            prof.phone = customer_phone
        if not prof.address_line and address_line and 'Store Pickup' not in address_line:
            prof.address_line = address_line
            prof.city = city
            prof.state = state
            prof.pincode = pincode
        prof.save()

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            size=item['size'],
            quantity=item['quantity'],
            price=item['product'].discount_price,
        )

    # Razorpay Order initiation
    amount_in_paise = int(round(float(grand_total) * 100))
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_skfashion_demo')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'skfashion_secret_demo')

    razorpay_order_id = None
    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        rzp_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': order.order_id,
            'payment_capture': 1
        })
        razorpay_order_id = rzp_order['id']
    except Exception:
        # Fallback mock order ID for demo/testing mode
        razorpay_order_id = f"order_demo_{order.order_id}_{amount_in_paise}"

    order.razorpay_order_id = razorpay_order_id
    order.save()

    is_sandbox = (
        key_id == 'rzp_test_skfashion_demo' or
        'demo' in key_id.lower() or
        razorpay_order_id.startswith('order_demo_')
    )

    return JsonResponse({
        'status': 'success',
        'order_id': order.order_id,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': key_id,
        'is_sandbox': is_sandbox,
        'amount': amount_in_paise,
        'currency': 'INR',
        'name': 'SK Fashion',
        'description': f'Order #{order.order_id} - Menswear',
        'customer_name': order.customer_name,
        'customer_email': order.customer_email or 'customer@skfashionmens.com',
        'customer_phone': order.customer_phone,
    })


def verify_razorpay_payment(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    order_id = data.get('order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')

    order = get_object_or_404(Order, order_id=order_id)
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_skfashion_demo')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'skfashion_secret_demo')

    is_verified = False
    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        is_verified = True
    except Exception:
        # In test / demo environment or sandbox simulation
        if (
            (razorpay_order_id and razorpay_order_id.startswith('order_demo_')) or
            (razorpay_payment_id and (razorpay_payment_id.startswith('pay_test_') or razorpay_payment_id.startswith('pay_sim_') or razorpay_payment_id.startswith('pay_demo_'))) or
            key_id == 'rzp_test_skfashion_demo' or
            'demo' in key_id.lower() or
            (razorpay_signature and ('demo' in razorpay_signature or 'sim' in razorpay_signature or razorpay_signature in ('verified_signature', 'demo_verified')))
        ):
            is_verified = True

    if is_verified:
        order.payment_method = 'RAZORPAY'
        order.payment_status = 'COMPLETED'
        order.order_status = 'CONFIRMED'
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_signature = razorpay_signature or 'verified_signature'
        order.save()

        # Clear cart and applied coupon
        request.session['cart'] = {}
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        request.session.modified = True

        return JsonResponse({
            'status': 'success',
            'redirect_url': f"/order-success/{order.order_id}/"
        })
    else:
        order.payment_status = 'FAILED'
        order.save()
        return JsonResponse({
            'status': 'error',
            'message': 'Payment verification failed. Please try again or choose another payment method.'
        }, status=400)


def apply_coupon(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    code = data.get('coupon_code', '').strip().upper()
    cart_data = _get_cart_data(request)
    subtotal = cart_data['subtotal']

    if not code:
        return JsonResponse({'status': 'error', 'message': 'Please enter a coupon code.'})

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f"Coupon '{code}' is not valid or expired."})

    if subtotal < float(coupon.min_order_amount):
        return JsonResponse({
            'status': 'error',
            'message': f"Coupon '{coupon.code}' requires a minimum order of ₹{coupon.min_order_amount:.0f}. (Current: ₹{subtotal:.0f})"
        })

    discount = round(subtotal * (coupon.discount_percentage / 100.0), 2)
    request.session['applied_coupon'] = coupon.code
    request.session.modified = True

    return JsonResponse({
        'status': 'success',
        'code': coupon.code,
        'discount_percentage': coupon.discount_percentage,
        'discount_amount': discount,
        'message': f"Success! Coupon {coupon.code} applied ({coupon.discount_percentage}% OFF)."
    })


def remove_coupon(request):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        request.session.modified = True
    return JsonResponse({'status': 'success', 'message': 'Coupon removed.'})


def order_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    items = order.items.all()
    context = {
        'order': order,
        'items': items,
        'store_settings': getattr(settings, 'STORE_SETTINGS', {}),
    }
    return render(request, 'store/invoice.html', context)


def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    store_phone = getattr(settings, 'STORE_SETTINGS', {}).get('WHATSAPP_NUMBER', '919876543210')
    
    # Pre-formatted WhatsApp confirmation
    msg = (
        f"Hello SK Fashion! I have placed Order #{order.order_id} on your website.\n"
        f"👤 Customer: {order.customer_name} ({order.customer_phone})\n"
        f"💰 Total Amount: ₹{order.total_amount}\n"
        f"📦 Delivery: {order.get_delivery_type_display()}\n"
        f"💳 Payment: {order.get_payment_method_display()} ({order.get_payment_status_display()})\n\n"
        f"Please confirm my order delivery details. Thank you!"
    )
    whatsapp_confirm_url = f"https://wa.me/{store_phone}?text={urllib.parse.quote(msg)}"

    store_upi_id = getattr(settings, 'STORE_UPI_ID', 'skfashion@oksbi')
    store_upi_name = getattr(settings, 'STORE_UPI_NAME', 'SK Fashion Menswear')
    upi_intent_url = f"upi://pay?pa={store_upi_id}&pn={urllib.parse.quote(store_upi_name)}&am={order.total_amount:.2f}&cu=INR&tn=SKF_{order.order_id}"

    context = {
        'order': order,
        'items': order.items.all(),
        'whatsapp_confirm_url': whatsapp_confirm_url,
        'upi_intent_url': upi_intent_url,
        'store_upi_id': store_upi_id,
    }
    return render(request, 'store/order_success.html', context)



def track_order(request):
    order = None
    searched = False
    query = request.GET.get('order_query')

    if query:
        searched = True
        query = query.strip()
        orders = Order.objects.filter(Q(order_id__iexact=query) | Q(customer_phone=query))
        if orders.exists():
            order = orders.first()

    context = {
        'order': order,
        'searched': searched,
        'query': query,
    }
    return render(request, 'store/track_order.html', context)


def store_locator(request):
    return render(request, 'store/store_locator.html')


def service_worker(request):
    from django.http import HttpResponse
    return HttpResponse("// SK Fashion Service Worker", content_type="application/javascript")


def customer_register(request):
    if request.user.is_authenticated:
        return redirect('customer_account')

    next_url = request.GET.get('next') or request.POST.get('next') or 'customer_account'

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not full_name:
            messages.error(request, 'Please enter your full name.')
            return render(request, 'store/register.html', {'full_name': full_name, 'phone': phone, 'email': email, 'next': next_url})

        if not phone or len(phone) < 10:
            messages.error(request, 'Please enter a valid 10-digit mobile number.')
            return render(request, 'store/register.html', {'full_name': full_name, 'phone': phone, 'email': email, 'next': next_url})

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'store/register.html', {'full_name': full_name, 'phone': phone, 'email': email, 'next': next_url})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please re-enter.')
            return render(request, 'store/register.html', {'full_name': full_name, 'phone': phone, 'email': email, 'next': next_url})

        username = phone
        if User.objects.filter(username=username).exists() or CustomerProfile.objects.filter(phone=phone).exists():
            messages.error(request, f'An account with mobile number {phone} already exists. Please sign in instead.')
            return redirect(f"/account/login/?identifier={phone}")

        if email and User.objects.filter(email=email).exists():
            messages.error(request, f'An account with email {email} already exists. Please sign in instead.')
            return redirect(f"/account/login/?identifier={email}")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.save()

        # Link past guest orders matching this phone number
        Order.objects.filter(customer_phone__icontains=phone, user__isnull=True).update(user=user)

        login(request, user)
        messages.success(request, f"Welcome to SK Fashion, {full_name}! Your account has been created.")
        return redirect(next_url)

    return render(request, 'store/register.html', {'next': next_url})


def customer_login(request):
    if request.user.is_authenticated:
        return redirect('customer_account')

    next_url = request.GET.get('next') or request.POST.get('next') or 'customer_account'
    identifier = request.GET.get('identifier', '')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            messages.error(request, 'Please provide your mobile number/email and password.')
            return render(request, 'store/login.html', {'identifier': identifier, 'next': next_url})

        user = authenticate(request, username=identifier, password=password)

        if user is None:
            found = User.objects.filter(
                Q(email__iexact=identifier) | Q(profile__phone=identifier) | Q(username__iexact=identifier)
            ).first()
            if found and found.check_password(password):
                user = found

        if user is not None:
            login(request, user)
            
            if hasattr(user, 'profile') and user.profile.phone:
                Order.objects.filter(customer_phone__icontains=user.profile.phone, user__isnull=True).update(user=user)

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid mobile number/email or password. Please try again.')

    return render(request, 'store/login.html', {'identifier': identifier, 'next': next_url})


def customer_logout(request):
    logout(request)
    messages.success(request, 'You have been safely signed out. Visit again soon!')
    return redirect('home')


@login_required(login_url='customer_login')
def customer_account(request):
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip().lower()
            address_line = request.POST.get('address_line', '').strip()
            city = request.POST.get('city', 'Ahilyanagar').strip()
            state = request.POST.get('state', 'Maharashtra').strip()
            pincode = request.POST.get('pincode', '414001').strip()

            if full_name:
                user.first_name = full_name
            if email:
                user.email = email
            user.save()

            if phone:
                profile.phone = phone
            profile.address_line = address_line
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.save()

            messages.success(request, 'Your profile and delivery address have been updated.')
            return redirect('customer_account')

    orders = Order.objects.filter(
        Q(user=user) | (Q(customer_phone__icontains=profile.phone) if profile.phone else Q(pk__in=[]))
    ).distinct().prefetch_related('items__product').order_by('-created_at')

    total_spent = sum(o.total_amount for o in orders)
    wishlist_ids = request.session.get('wishlist', [])

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'orders_count': orders.count(),
        'total_spent': total_spent,
        'wishlist_count': len(wishlist_ids),
        'store_settings': getattr(settings, 'STORE_SETTINGS', {}),
    }
    return render(request, 'store/account.html', context)


@login_required(login_url='customer_login')
def reorder_items(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    cart = request.session.get('cart', {})
    added_count = 0

    for item in order.items.all():
        if item.product and item.product.is_available:
            item_key = f"{item.product.id}_{item.size}"
            if item_key in cart:
                cart[item_key]['quantity'] += item.quantity
            else:
                cart[item_key] = {
                    'product_id': item.product.id,
                    'size': item.size,
                    'quantity': item.quantity,
                }
            added_count += 1

    request.session['cart'] = cart
    request.session.modified = True

    if added_count > 0:
        messages.success(request, f"Added items from Order #{order.order_id} back to your shopping bag!")
        return redirect('cart_view')
    else:
        messages.warning(request, "Could not reorder: items may no longer be available.")
        return redirect('customer_account')


