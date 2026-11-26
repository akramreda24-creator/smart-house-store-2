from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/products/", views.dashboard_products, name="dashboard_products"),
    path("dashboard/products/add/", views.dashboard_product_add, name="dashboard_product_add"),
    path("dashboard/products/<int:pk>/edit/", views.dashboard_product_edit, name="dashboard_product_edit"),
    path("dashboard/products/<int:pk>/delete/", views.dashboard_product_delete, name="dashboard_product_delete"),
    path("dashboard/orders/", views.dashboard_orders, name="dashboard_orders"),
    path("dashboard/orders/<int:pk>/", views.dashboard_order_detail, name="dashboard_order_detail"),
    path("dashboard/customers/", views.dashboard_customers, name="dashboard_customers"),
    path("dashboard/orders/<int:pk>/status/", views.dashboard_order_status, name="dashboard_order_status"),
    path("", views.home, name="home"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("contact/", views.contact, name="contact"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
