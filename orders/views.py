from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.exceptions import ValidationError

from cart.models import CartItem
from products.models import Product
from .models import Order, OrderItem


@login_required
def checkout(request):
    items = list(
        CartItem.objects.filter(
            user=request.user
        ).select_related('product')
    )

    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    total = sum(
        (item.product.price * item.quantity for item in items),
        start=Decimal('0.00')
    )

    if request.method == 'POST':
        try:
            with transaction.atomic():
                locked_items = list(
                    CartItem.objects.filter(
                        user=request.user
                    ).select_related('product')
                )

                if not locked_items:
                    raise ValidationError('Your cart is empty.')

                product_ids = sorted({
                    item.product_id for item in locked_items
                })

                locked_products = {
                    product.id: product
                    for product in Product.objects.select_for_update()
                    .filter(id__in=product_ids).order_by('id')
                }

                order_total = Decimal('0.00')

                for item in locked_items:
                    product = locked_products.get(item.product_id)

                    if product is None:
                        raise ValidationError(
                            'A product in your cart is unavailable.'
                        )

                    if item.quantity < 1 or item.quantity > product.quantity:
                        raise ValidationError(
                            f'Not enough stock for {product.name}.'
                        )

                    order_total += product.price * item.quantity

                order = Order.objects.create(
                    user=request.user,
                    total_amount=order_total
                )

                for item in locked_items:
                    product = locked_products[item.product_id]

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item.quantity
                    )

                    product.quantity -= item.quantity
                    product.save(update_fields=['quantity'])

                CartItem.objects.filter(
                    user=request.user
                ).delete()

        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
            return redirect('cart_detail')

        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'items': items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.user
    )

    return render(request, 'order_success.html', {
        'order': order,
    })


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )

    return render(request, 'order_history.html', {
        'orders': orders,
    })