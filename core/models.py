from django.db import models
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField  # pip install shortuuid
from django.utils.html import mark_safe
from django.contrib.auth.models import User

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
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, primary_key=True)
    title = models.CharField(max_length=100, default="No title provided")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        
    def __str__(self):
        return self.title
        
class Tags(models.Model):
    pass
        
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, primary_key=True)

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(null=True, blank=True, default="No description provided")

    address = models.CharField(max_length=255, null=True, blank=True, default="No address provided")
    contact = models.CharField(max_length=100, null=True, blank=True, default="No contact info provided")
    chat_resp_time = models.CharField(max_length=100, null=True, blank=True, default="No response time provided")
    shippingon_time = models.CharField(max_length=100, null=True, blank=True, default="No shipping info provided")
    authenticrating = models.CharField(max_length=100, null=True, blank=True, default="No rating info provided")
    days_return = models.CharField(max_length=100, null=True, blank=True, default="No return info provided")
    warranty_period = models.CharField(max_length=100, null=True, blank=True, default="No warranty info provided")

    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        
    def __str__(self):
        return self.title
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, primary_key=True)

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, default='product.jpg')
    description = models.TextField(null=True, blank=True, default="No description provided")
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    specifications = models.TextField(null=True, blank=True, default="No specifications provided")
    tags = models.ForeignKey(Tags, on_delete=models.CASCADE, null=True, blank=True)

    product_status = models.CharField(max_length=20, choices=STATUS, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="SKU-", alphabet="0123456789")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        
    def __str__(self):
        return self.title
        
    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
        
class ProductImages(models.Model):
    images = models.ImageField(upload_to='product_images/', blank=True, null=True, default='product.jpg')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"


####################### CART MODELS #########################

class CartOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=100)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_image(self):
        return mark_safe(f'<img src="/media/%s" width="50" height="50" />' % (self.image))
        

######################## Product Review, Wishlists, Address ########################

class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING, default=None)
    review = models.TextField(null=True, blank=True, default="No review provided")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"
        
    def __str__(self):
        return self.product
        
    def get_rating(self):
        return self.rating
        
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING, default=None)
    review = models.TextField(null=True, blank=True, default="No review provided")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"
        
    def __str__(self):
        return self.product
        
    def get_rating(self):
        return self.rating
        
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, default="No address provided", null=True)
    status = models.BooleanField(default=False)


############################# PTC Bucks ###################################

class PTCCurrency(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.balance} PTC Bucks"

class PTCCurrencyTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=(
            ('credit', 'Credit'),
            ('debit', 'Debit')
        )
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.amount} ({self.transaction_type})"

        