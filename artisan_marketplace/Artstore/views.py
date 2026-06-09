from django.http import HttpResponse
from django.shortcuts import render
from .models import *

# Create your views here.
def homeadmin(request):
    return render(request,'admin/Adminhome.html')

def log(request):
    return render(request,'login.html')

def log_post(request):
    username = request.POST['textfield']
    password = request.POST['textfield2']
    return HttpResponse("login success")

def changepass(request):
    return render(request,'admin/change_pass.html')

def changepass_post(request):
    currentpassword = request.POST['textfield']
    newpassword = request.POST['textfield2']
    confirmpassword = request.POST['textfield3']
    return HttpResponse("password changed successfully")

def addcategory(request):
    return render(request,'admin/add_category.html')

def addcategory_post(request):
    categorys = request.POST['textfield']
    obj = category()
    obj.category = categorys
    obj.save()
    return HttpResponse("success")

def editcategory(request,id):
    data = category.objects.get(id=id)
    return render(request,'admin/edit_category.html',{"data":data,"id":id})

def editcategory_post(request,id):
    categorys = request.POST['textfield']
    category.objects.filter(id=id).update(category=categorys)
    return HttpResponse("success")

def viewartisan(request):
    data = artisan.objects.all()
    return render(request,'admin/view_artisan.html',{"data":data})

def viewcategory(request):
    data = category.objects.all()
    return render(request,'admin/view_category.html',{"data":data})

def viewcustomer(request):
    data = customer.objects.all()
    return render(request,'admin/view_customer.html',{"data":data})


def viewcomplaint(request):
    data = complaint.objects.all()
    return render(request,'admin/view_complaint.html',{"data":data})


def viewfeedback(request):
    data = feedback.objects.all()
    return render (request,'admin/view_feedback.html',{"data":data})


def replycomplaint(request):
    return render(request,'admin/replycomplaint.html')

def replycomplaint_post(request):
    reply = request.POST['textarea']
    return HttpResponse("success")

def logout(request):
    return HttpResponse("Logout")

def deletecategory(request,id):
    category.objects.get(id=id).delete()
    return HttpResponse("Deleted")


