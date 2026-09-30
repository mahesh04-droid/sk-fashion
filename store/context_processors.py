from django.conf import settings
from .models import Category


def store_context(request):
    """
    Context processor to make store settings, categories, and cart count
    globally available to all templates.
    """
    categories = Category.objects.all()[:8]
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    wishlist = request.session.get('wishlist', [])
    wishlist_count = len(wishlist)
    wishlist_ids = set(wishlist)

    return {
        'store_settings': getattr(settings, 'STORE_SETTINGS', {}),
        'nav_categories': categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'wishlist_ids': wishlist_ids,
    }
