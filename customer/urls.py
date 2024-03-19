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
# from django.shortcuts import HttpResponse, render, redirect
from django.conf.urls import url

# from django.contrib import admin
# from django.urls import path
from customer import views

urlpatterns = [
    url(r'^index.html$', views.index),
    url(r'^searchcom', views.dosearch, name="com_search"),  # 客户端搜索商品
    url(r'^searchcars', views.searchcars),  # 客户端查看已有的购物车
]
