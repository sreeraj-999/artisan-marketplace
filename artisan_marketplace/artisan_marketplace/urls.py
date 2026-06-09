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
    path('replycomplaint',views.replycomplaint),
    path('log_post', views.log_post),
    path('changepass_post',views.changepass_post),
    path('addcategory_post',views.addcategory_post),
    path('editcategory_post/<id>',views.editcategory_post),
    path('replycomplaint_post',views.replycomplaint_post),
    path('logout',views.logout),
    path('deletecategory/<id>',views.deletecategory),

]
