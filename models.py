from django.db import models
from shortuuid.django_fields import ShortUUIDField #pip install shortuuid
from django.utils.html import mark_safe
from userauths.models import User

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
    cid = models.UUIDField(unique = True, length = 10, max_length = 30, prefix = "cat",
                            alphabet = "abcdefghijklmnopqrstuvwxyz123456789",)
    title = models.CharField(max_lnegth = 100)
    image = models.ImageField(upload_to="category", default = "category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
class Tags(models.Model):
    pass

class Vendor(models.Model):
    vid = models.UUIDField(unique = True, length = 10, max_length = 30, prefix = "ven",
                            alphabet = "abcdefghijklmnopqrstuvwxyz123456789",)
    title = models.CharField(max_lnegth = "El Condor Pasa")
    image = models.ImageField(upload_to= user_directory_path, default= "vendor.jpg")
    description = models.TextField(null=True, black=True, default = "I think therefore I am")


    address = models.CharField(max_length=100, default="123 main street")
    contact = models.CharField(max_length=100, default="+123 (456) 789")
    chat_resp_time = models.CharField(max_length=100, default="1")
    shipping_on_time = models.CharField(max_length=100, default="1")
    authetic_rating = models.CharField(max_length=100, default="1")
    days_return = models.CharField(max_length=100, default="1")
    warranty_period = models.CharField(max_length=100, default="1")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title
    
class Product(models.Model):
    pid = models.UUIDField(unique = True, length = 10, max_length = 30, alphabet = "abcdefghijklmnopqrstuvwxyz123456789",)
    
    title = models.CharField(max_lnegth = "Fresh Pear")
    image = models.ImageField(upload_to= user_directory_path, default= "product.jpg")
    description = models.TextField(null=True, black=True, default = "this is product")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category= models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)
    old_price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)

    specifications = models.TextField(null=True, blank=True)
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = models.UUIDField(unique = True, length = 4, max_length = 10, prefix="sku", alphabet = "123456789",)

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width = "50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_percentage(self):
        new_price = (self.price / self.old_price) *100
        return new_price
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Images"

###################### cart, order, orderitems#########################

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=99999999999999999, decimal_places=2)
    total = models.DecimalField(max_digits=99999999999999999, decimal_places=2)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width = "50" height = "50" />' % (self.image.url))

###################### product review, wishlist, address#########################

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating  

class wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "wishlists"

    def __str__(self):
        return self.product.title
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "address"