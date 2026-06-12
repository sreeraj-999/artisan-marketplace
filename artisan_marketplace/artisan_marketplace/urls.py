"""artisan_marketplace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from Artstore import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homeadmin),
    path('log',views.log),
    path('changepass',views.changepass),
    path('addcategory',views.addcategory),
    path('editcategory/<id>',views.editcategory),
    path('viewartisan',views.viewartisan),
    path('viewcategory',views.viewcategory),
    path('viewcustomer',views.viewcustomer),
    path('viewcomplaint',views.viewcomplaint),
    path('viewfeedback',views.viewfeedback),
    
    # Updated reply complaint paths to include complaint ID
    path('replycomplaint/<id>',views.replycomplaint),
    path('replycomplaint_post/<id>',views.replycomplaint_post),
    
    # Block/Unblock Artisans
    path('blockartisan/<id>',views.blockartisan),
    path('unblockartisan/<id>',views.unblockartisan),
    
    path('log_post', views.log_post),
    path('changepass_post',views.changepass_post),
    path('addcategory_post',views.addcategory_post),
    path('editcategory_post/<id>',views.editcategory_post),
    path('logout',views.logout),
    path('deletecategory/<id>',views.deletecategory),

    # Artisan Module Routes
    path('artisan_signup', views.artisan_signup),
    path('artisan_signup_post', views.artisan_signup_post),
    path('artisan_home', views.artisan_home),
    path('artisan_profile', views.artisan_profile),
    path('artisan_profile_post', views.artisan_profile_post),
    
    # Artisan Products Catalog
    path('artisan_addproduct', views.artisan_addproduct),
    path('artisan_addproduct_post', views.artisan_addproduct_post),
    path('artisan_viewproducts', views.artisan_viewproducts),
    path('artisan_editproduct/<id>', views.artisan_editproduct),
    path('artisan_editproduct_post/<id>', views.artisan_editproduct_post),
    path('artisan_deleteproduct/<id>', views.artisan_deleteproduct),
    
    # Artisan Orders, Payments, Reviews
    path('artisan_vieworders', views.artisan_vieworders),
    path('artisan_updateorderstatus/<id>', views.artisan_updateorderstatus),
    path('artisan_viewpayments', views.artisan_viewpayments),
    path('artisan_viewreviews', views.artisan_viewreviews),
    
    # Artisan Chat System
    path('artisan_chat', views.artisan_chat),
    path('artisan_chatroom/<customer_id>', views.artisan_chatroom),
    path('artisan_chat_send/<customer_id>', views.artisan_chat_send),

    # Customer Module Routes
    path('customer_signup', views.customer_signup),
    path('customer_signup_post', views.customer_signup_post),
    path('customer_home', views.customer_home),
    path('customer_viewproducts', views.customer_viewproducts),
    path('customer_follow_artisan/<artisan_id>', views.customer_follow_artisan),
    path('customer_viewcart', views.customer_viewcart),
    path('customer_addto_cart/<product_id>', views.customer_addto_cart),
    path('customer_remove_cart/<cart_id>', views.customer_remove_cart),
    path('customer_checkout', views.customer_checkout),
    path('customer_place_order', views.customer_place_order),
    path('customer_vieworders', views.customer_vieworders),
    path('customer_addfeedback/<product_id>', views.customer_addfeedback),
    path('customer_addfeedback_post/<product_id>', views.customer_addfeedback_post),
    path('customer_addcomplaint', views.customer_addcomplaint),
    path('customer_addcomplaint_post', views.customer_addcomplaint_post),
    path('customer_viewcomplaints', views.customer_viewcomplaints),
    path('customer_chat', views.customer_chat),
    path('customer_chatroom/<artisan_id>', views.customer_chatroom),
    path('customer_chat_send/<artisan_id>', views.customer_chat_send),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
