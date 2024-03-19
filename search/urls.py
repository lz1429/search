"""search URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.shortcuts import HttpResponse, render, redirect
from django.conf.urls import url, include


def default(request):
    print("访问的URL需要具体些")
    return render(request, 'admin/404.html')


urlpatterns = [
    url(r'^admin/', include('adminpg.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^', default)
]
