from django.db import models
from django.core import validators
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self,username,email,telephone,password=None,**extra_fields):
        if not email:
            raise ValueError('The Email Most Be Set')
        if not telephone:
            raise ValueError('Telephone Most Be Set')
        
        email = self.normalize_email(email)
        user = self.model(username=username,email=email,telephone=telephone,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,username,email,telephone,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser Must Have is_staff True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser Must Have is_superuser True')

        return self.create_user(username,email,telephone,password,**extra_fields)


class UserAccount(AbstractUser):
    regex = RegexValidator(r"^(?:0|98|\+98|\+980|0098|098|00980)?(9\d{9})$")
    email = models.EmailField(max_length=255,unique=True)
    telephone = models.PositiveBigIntegerField(unique=True,validators=[regex])

    REQUIRED_FIELDS = ['email','telephone']
    objects = UserManager()


class UserAddress(models.Model):
    user = models.OneToOneField(UserAccount,on_delete=models.CASCADE)
    city = models.CharField(max_length=55)
    post_address = models.PositiveBigIntegerField(unique=True)
    address = models.TextField(max_length=12500)

    @property
    def shortAddress(self):
        return self.address[:30]


class Product(models.Model):
    choice = [
        ('Digital','Digital'),
        ('Makeup','Makeup'),
        ('Stationery','Stationery'),
        ('Health','Health'),
        ('Perfume','Perfume')
    ]
    category = models.CharField(max_length=10,choices=choice)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    review = models.TextField()
    performance = models.TextField(max_length=6500)
    image = models.ImageField(upload_to='products/')
    product_exists = models.BooleanField(verbose_name='Product Exist',default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.SET_NULL,blank=True,null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
    
    @property
    def username(self):
        return str(self.user)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
    quantity = models.PositiveSmallIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    

class Payment(models.Model):
    user = models.ForeignKey(UserAccount,on_delete=models.RESTRICT)
    cart = models.OneToOneField(Order,on_delete=models.RESTRICT)
    payed = models.BooleanField(default=False)
    buyed_time = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    message = models.TextField(max_length=12500)

    @property
    def shortmessage(self):
        return self.message[:30]