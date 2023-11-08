from django.contrib import admin

from . import models


@admin.register(models.UserAccount)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username','email','telephone','is_active','is_staff','is_superuser']


@admin.register(models.UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user','city','post_address','shortAddress']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','product_exists']


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','date_ordered','complete']


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product','order','quantity','date_added']


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user','cart','payed','buyed_time']


@admin.register(models.Contact)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['name','email','shortmessage']
