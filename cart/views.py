from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction

from products.models import Product
from .models import CartItem


@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        messages.error(request, 'Invalid quantity.')
        return redirect('product_detail', id=product.id)

    if quantity < 1:
        messages.error(request, 'Quantity must be at least 1.')
        return redirect('product_detail', id=product.id)

    if product.quantity < quantity:
        messages.error(request, 'Not enough stock available.')
        return redirect('product_detail', id=product.id)

    with transaction.atomic():
        item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            item.quantity += quantity

            if item.quantity > product.quantity:
                messages.error(request, 'Not enough stock available.')
                return redirect('cart_detail')

            item.save(update_fields=['quantity'])

    messages.success(request, 'Product added to cart!')
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    items = CartItem.objects.filter(
        user=request.user
    ).select_related('product')

    total = sum(
        (item.subtotal for item in items),
        start=0
    )

    return render(request, 'cart_detail.html', {
        'items': items,
        'total': total,
    })



@login_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    action = request.POST.get('action')

    if action == 'increase':
        if item.quantity < item.product.quantity:
            item.quantity += 1
            item.save(update_fields=['quantity'])
        else:
            messages.error(request, 'Not enough stock available.')

    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save(update_fields=['quantity'])
        else:
            item.delete()

    return redirect('cart_detail')


@login_required
@require_POST
def cart_remove(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )
    item.delete()

    messages.success(request, 'Item removed from cart.')
    return redirect('cart_detail')