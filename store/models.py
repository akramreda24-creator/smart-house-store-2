from django.db import models

class Product(models.Model):
    name = models.CharField("اسم المنتج", max_length=180)
    slug = models.SlugField("الرابط المختصر", max_length=200, unique=True)
    description = models.TextField("الوصف", blank=True)
    price = models.DecimalField("السعر", max_digits=10, decimal_places=2)
    sale_price = models.DecimalField("سعر العرض", max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField("صورة المنتج", upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField("ظاهر في المتجر", default=True)
    is_featured = models.BooleanField("منتج مميز", default=False)
    stock = models.PositiveIntegerField("المخزون", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.sale_price if self.sale_price is not None else self.price


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "جديد"), ("confirmed", "تم التأكيد"),
        ("shipped", "تم الشحن"), ("completed", "مكتمل"),
        ("cancelled", "ملغي"),
    ]
    customer_name = models.CharField("اسم العميل", max_length=150)
    phone = models.CharField("رقم الهاتف", max_length=30)
    address = models.TextField("العنوان")
    notes = models.TextField("ملاحظات", blank=True)
    status = models.CharField("حالة الطلب", max_length=20, choices=STATUS_CHOICES, default="new")
    total = models.DecimalField("الإجمالي", max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField("تاريخ الطلب", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f"طلب #{self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="المنتج")
    quantity = models.PositiveIntegerField("الكمية")
    unit_price = models.DecimalField("سعر الوحدة", max_digits=10, decimal_places=2)
