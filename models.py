from django.db import models
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField  # pip install shortuuid
from django.utils.html import mark_safe

#NOTE: remember to pip install Pillow !!!

STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)
STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)
RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

def user_directory_path(instance, filename):
    # stores files under user_<id>/filename
    user_id = getattr(instance.user, "id", "anonymous")
    return f'user_{user_id}/{filename}'

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

class Tags(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, default="vendor.jpg")
    description = models.TextField(null=True, blank=True, default="I think therefore I am")

    address = models.CharField(max_length=100, default="123 main street")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    chat_resp_time = models.CharField(max_length=100, default="1")
    shipping_on_time = models.CharField(max_length=100, default="1")
    authetic_rating = models.CharField(max_length=100, default="1")
    days_return = models.CharField(max_length=100, default="1")
    warranty_period = models.CharField(max_length=100, default="1")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default="This is a product")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    # reasonable limits for prices
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    specifications = models.TextField(null=True, blank=True)
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True, blank=True)

    product_status = models.CharField(choices=STATUS, max_length=20, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="123456789")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.title

    def get_percentage(self):
        try:
            if self.old_price and float(self.old_price) > 0:
                new_price = (float(self.price) / float(self.old_price)) * 100
                return new_price
        except Exception:
            return None
        return None

class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="images")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

###################### cart, order, orderitems#########################

class CartOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name="items")
    product_status = models.CharField(max_length=200, null=True, blank=True)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        # image is a path stored as string, so can't call .url directly
        return mark_safe(f'<img src="/media/{self.image}" width="50" height="50" />')

###################### product review, wishlist, address#########################

class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title if self.product else "Review"

    def get_rating(self):
        return self.rating

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.title if self.product else "Wishlist Item"

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "address"
