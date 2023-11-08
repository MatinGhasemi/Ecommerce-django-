from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('accounts/register/',views.Register.as_view(),name='register'),
    path('',views.Home.as_view(),name='home'),
    path('user_page/',login_required(views.UserPage.as_view()),name='user-page'),
    path('new_address/',login_required(views.NewAddress.as_view()),name='new-address'),
    path('user_page/update_address/',login_required(views.UpdateAddress.as_view()),name='update-address'),
    path('user_page/update_user/',login_required(views.UpdateUser.as_view()),name='update-user'),
    path('product/<int:id>/',views.ProductDetail.as_view(),name='detail-view'),
    path('product/category/<str:category>/',views.ProductCategory.as_view(),name='category-view'),
    path('product/search_results/',views.SearchProduct.as_view(),name='search-results'),
    path('update_item/',views.updateItem,name='update_item'),
    path('cart/',views.Cart.as_view(),name='cart'),
    path('cart/AnonymousUserPayment',views.LoginAndPay.as_view(),name='login-pay'),
    path('contactus/',views.Contact.as_view(),name='contact')
]
