from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Product
from .forms import ProductForm


def staff_required(view_func):
    return user_passes_test(
        lambda user: user.is_active and user.is_staff
    )(view_func)



@login_required
def product_list(request):
    
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()

    products = Product.objects.all().order_by('-created_at')

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(category__icontains=search)
        )

    if category:
        products = products.filter(
            category__iexact=category
        )

    categories = (
        Product.objects.order_by('category')
        .values_list('category', flat=True)
        .distinct()
    )

    paginator = Paginator(products, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'product_list.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'search': search,
        'category': category,
        'categories': categories,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    return render(request, 'product_detail.html', {
        'product': product,
    })


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {
        'form': form,
        'title': 'Add Product',
    })


@staff_required
def product_update(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {
        'form': form,
        'title': 'Update Product',
    })


@staff_required
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')

    return render(request, 'product_delete.html', {
        'product': product,
    })