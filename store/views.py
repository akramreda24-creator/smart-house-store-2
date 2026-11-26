from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Product, Order, OrderItem

def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "store/home.html", {
        "products": products,
        "featured": products.filter(is_featured=True)[:4],
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = request.session.get("cart", {})
    key = str(product.pk)
    cart[key] = int(cart.get(key, 0)) + 1
    request.session["cart"] = cart
    messages.success(request, "تمت إضافة المنتج إلى السلة.")
    return redirect(request.META.get("HTTP_REFERER", "cart"))

@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart")

def cart(request):
    cart_data = request.session.get("cart", {})
    items, total = [], Decimal("0.00")
    for product_id, quantity in cart_data.items():
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if product:
            subtotal = product.current_price * int(quantity)
            items.append({"product": product, "quantity": int(quantity), "subtotal": subtotal})
            total += subtotal
    return render(request, "store/cart.html", {"items": items, "total": total})

def checkout(request):
    cart_data = request.session.get("cart", {})
    if request.method == "POST":
        if not cart_data:
            messages.error(request, "السلة فارغة.")
            return redirect("cart")
        name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        notes = request.POST.get("notes", "").strip()
        if not name or not phone or not address:
            messages.error(request, "من فضلك أكمل الاسم ورقم الهاتف والعنوان.")
            return redirect("checkout")
        order = Order.objects.create(customer_name=name, phone=phone, address=address, notes=notes)
        total = Decimal("0.00")
        for product_id, quantity in cart_data.items():
            product = Product.objects.filter(pk=product_id, is_active=True).first()
            if product and int(quantity) > 0:
                price = product.current_price
                OrderItem.objects.create(order=order, product=product, quantity=int(quantity), unit_price=price)
                total += price * int(quantity)
        order.total = total
        order.save(update_fields=["total"])
        request.session["cart"] = {}
        return render(request, "store/order_success.html", {"order": order})
    return render(request, "store/checkout.html")

def contact(request):
    return render(request, "store/contact.html")


# ---------------- Custom Smart House dashboard ----------------
from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import ModelForm
from django.utils.text import slugify
from django.db.models import Sum, Count, Q
from .models import Product, Order

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["name", "slug", "description", "price", "sale_price",
                  "image", "stock", "is_active", "is_featured"]

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff,
                            login_url="/admin/login/")(view_func)

@staff_required
def dashboard(request):
    completed_revenue = Order.objects.exclude(status="cancelled").aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    context = {
        "products_count": Product.objects.count(),
        "orders_count": Order.objects.count(),
        "new_orders_count": Order.objects.filter(status="new").count(),
        "completed_revenue": completed_revenue,
        "low_stock_products": Product.objects.filter(is_active=True, stock__lte=5).order_by("stock")[:8],
        "recent_orders": Order.objects.all()[:8],
    }
    return render(request, "store/dashboard/home.html", context)

@staff_required
def dashboard_products(request):
    products = Product.objects.all()
    query = request.GET.get("q", "").strip()
    visibility = request.GET.get("visibility", "")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(slug__icontains=query))
    if visibility == "active":
        products = products.filter(is_active=True)
    elif visibility == "hidden":
        products = products.filter(is_active=False)
    elif visibility == "low":
        products = products.filter(stock__lte=5)
    return render(request, "store/dashboard/products.html", {"products": products, "query": query, "visibility": visibility})

@staff_required
def dashboard_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name, allow_unicode=True) or f"product-{Product.objects.count()+1}"
            product.save()
            messages.success(request, "تمت إضافة المنتج بنجاح.")
            return redirect("dashboard_products")
    else:
        form = ProductForm()
    return render(request, "store/dashboard/product_form.html", {"form": form, "page_title": "إضافة منتج جديد"})

@staff_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المنتج بنجاح.")
            return redirect("dashboard_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "store/dashboard/product_form.html", {"form": form, "page_title": "تعديل المنتج"})

@staff_required
@require_POST
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "تم حذف المنتج.")
    return redirect("dashboard_products")

@staff_required
def dashboard_orders(request):
    orders = Order.objects.prefetch_related("items__product").all()
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        if query.isdigit():
            orders = orders.filter(Q(pk=int(query)) | Q(phone__icontains=query) | Q(customer_name__icontains=query))
        else:
            orders = orders.filter(Q(customer_name__icontains=query) | Q(phone__icontains=query))
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)
    return render(request, "store/dashboard/orders.html", {"orders": orders, "query": query, "selected_status": status})

@staff_required
def dashboard_order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    return render(request, "store/dashboard/order_detail.html", {"order": order})

@staff_required
def dashboard_customers(request):
    customers = Order.objects.values("customer_name", "phone", "address").annotate(
        orders_count=Count("id"), total_spent=Sum("total")
    ).order_by("-orders_count")
    query = request.GET.get("q", "").strip()
    if query:
        customers = customers.filter(Q(customer_name__icontains=query) | Q(phone__icontains=query))
    return render(request, "store/dashboard/customers.html", {"customers": customers, "query": query})

@staff_required
@require_POST
def dashboard_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status")
    valid_statuses = dict(Order.STATUS_CHOICES)
    if status in valid_statuses:
        order.status = status
        order.save(update_fields=["status"])
        messages.success(request, f"تم تحديث حالة الطلب #{order.pk}.")
    else:
        messages.error(request, "حالة الطلب غير صحيحة.")
    return redirect("dashboard_orders")
