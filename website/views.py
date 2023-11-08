import json

from django.shortcuts import render,redirect
from django.db.models import Q
from django.views import View
from django.contrib import messages
from django.views.generic import ListView,FormView
from django.contrib.auth import authenticate,login
from django.urls import reverse
from django.http import HttpResponse, JsonResponse

from . import forms,models

class Register(View):

    def get(self,request):
        form = forms.RegisterUserForm()
        return render(request,'website/register.html',{'form':form})
    def post(self,request):
        form = forms.RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,f'User {username} Added !')
            return redirect(reverse('new-address'))
        messages.error(request,form.errors)
        return render(request,'website/register.html',{'form':form})
        

class Home(View):
    def get(self,request):
        products = models.Product.objects.all().order_by('-create_at')
        return render(request,'website/home.html',{'products':products})
    

class NewAddress(View):
    def get(self,request):
        address_exists = models.UserAddress.objects.filter(user=request.user).first()
        if address_exists:
            return redirect(reverse('user-page'))
        form = forms.UserAddressForm()
        return render(request,'website/new_address.html',{'form':form}) 

    def post(self,request):
        form = forms.UserAddressForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.user = request.user
            f.save()
            return redirect(reverse('user-page'))
        return render(request,'website/new_address.html',{'form':form})


class UserPage(View):
    def get(self,request):
        user = models.UserAddress.objects.filter(user=request.user).first()
        if user is None:
            return redirect(reverse('new-address'))
        orders = user.user.order_set.filter(complete=True)
        
        context = {'orders':orders,'user':user}
        return render(request,'website/user_page.html',context=context)
    

class UpdateAddress(View):
    def get(self,request):
        form = forms.UserAddressForm(instance=request.user.useraddress)
        return render(request,'website/update_address.html',{'form':form})

    def post(self,request):
        form = forms.UserAddressForm(request.POST,instance=request.user.useraddress)
        if form.is_valid():
            form.save()
            return redirect(reverse('user-page'))
        messages.error(request,form.errors)
        return render(request,'website/update_address.html',{'form':form})


class UpdateUser(View):
    def get(self,request):
        form = forms.UpdateUserForm(instance=request.user)
        return render(request,'website/update_user.html',{'form':form})
    def post(self,request):
        form = forms.UpdateUserForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('user-page'))
        messages.error(request,form.errors)
        return render(request,'website/update_user.html',{'form':form})
        

class ProductDetail(View):
    def get(self,request,id):
        try:
            product = models.Product.objects.get(id=id)
        except:
            return render(request,'website/error_404.html')
        return render(request,'website/detail_view.html',{'product':product})

class ProductCategory(View):
    def get(self,request,category):
        product = models.Product.objects.filter(category=category)
        return render(request,'website/category_view.html',{'products':product})
    

class SearchProduct(ListView):
    model = models.Product
    template_name = 'website/result.html'
    context_object_name = 'object'

    def get_queryset(self):
        query = self.request.GET.get('query')
        object_list = models.Product.objects.filter(Q(name__icontains=query) | Q(category__icontains=query))
        return object_list
    

class Cart(View):
    def get(self,request):
        if request.user.is_authenticated:
            order,created = models.Order.objects.get_or_create(user=request.user,complete=False)
            items = order.orderitem_set.all()
            cartitems = order.get_cart_items
        else:
            try:
                cart = json.loads(request.COOKIES['cart'])
            except:
                cart = {}
                
            items = []
            order = {'get_cart_total':0,'get_cart_items':0}
            cartitems = order['get_cart_items']
            for i in cart:
                cartitems += cart[i]['quantity']
                product = models.Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL
                    },
                    'quantity':cart[i]['quantity'],
                    'get_total':total
                }
                items.append(item)
            
        context = {'items':items,'order':order,'cartitems':cartitems}
    
        return render(request,'website/cart.html',context)
    
    def post(self,request):
        if request.user.is_authenticated:
            pk = models.Order.objects.filter(user=request.user).values_list('id',flat=True).last()
            
            models.Order.objects.filter(id=pk).update(complete=True)
            order = models.Order.objects.get(id=pk)
            
            models.Payment.objects.create(user=request.user,cart=order,payed=True).save()
            
            return redirect(reverse('user-page'))

        else:    
            return render(request,'website/error_404.html')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    product = models.Product.objects.get(id=productId)
    order,created = models.Order.objects.get_or_create(user=request.user,complete=False)
    orderitem,created = models.OrderItem.objects.get_or_create(order=order,product=product)

    if action=='add':
        orderitem.quantity = (orderitem.quantity+1)
    if action=='remove':
        orderitem.quantity = (orderitem.quantity-1)
    orderitem.save()

    if orderitem.quantity<=0:
        orderitem.delete()

    return JsonResponse('It Was Added',safe=False)


class LoginAndPay(View):
    def get(self,request):
        registerform = forms.RegisterUserForm()
        addressform = forms.UserAddressForm()
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
            
        items = []
        order = {'get_cart_total':0,'get_cart_items':0}
        cartitems = order['get_cart_items']
        for i in cart:
            cartitems += cart[i]['quantity']
            product = models.Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL
                },
                'quantity':cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)

        context = {'items':items,'order':order,'cartitems':cartitems,'registerform':registerform,'addressfrom':addressform}
        return render(request,'website/login_pay.html',context=context)
    
    def post(self,request):
        registerform = forms.RegisterUserForm(request.POST)
        addressform = forms.UserAddressForm(request.POST)
        
        if registerform.is_valid() and addressform.is_valid():
            registerform.save()
            username1 = registerform.cleaned_data['username']            
            addressform_commit = addressform.save(commit=False)
            username = models.UserAccount.objects.get(username=username1)
            addressform_commit.user = username
            addressform_commit.save()

            order = models.Order.objects.create(user=username,complete=True)
            order.save()

            try:
                cart = json.loads(request.COOKIES['cart'])
            except:
                cart = {}

            for i in cart:
                product = models.Product.objects.get(id=i)
                models.OrderItem.objects.create(product=product,order=order,quantity=cart[i]['quantity'])

            models.Payment.objects.create(user=username,cart=order,payed=True)

            password = registerform.cleaned_data['password1']
            user = authenticate(username=username1,password=password)
            login(request,user)
            return redirect(reverse('user-page'))

        messages.error(request,registerform.errors)
        return redirect(reverse('cart'))



class Contact(FormView):
    template_name = 'website/contact.html'
    form_class = forms.ContactForm

    def form_valid(self, form):
        messages.success(self.request,"Your Message Successfully Saved We Will Answer Soon As Sonn Its Posible")
        form.save()
        return redirect(reverse('home'))

    def form_invalid(self, form):
        messages.error(self.request,form.errors)
        return redirect(reverse('contact'))    