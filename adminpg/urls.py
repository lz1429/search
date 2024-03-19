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
from adminpg import views
from django.conf.urls import url

urlpatterns = [
    url(r'^index.html$', views.index, name="index"),  # 后台首页
    url(r'^layout$', views.layout),  # 母版
    # url(r'^verify', views.verify),  # 验证是否登录

    # 登录相关
    url(r'^login.html$', views.login, name="login"),  # 登录
    url(r'^reset.html$', views.resetpasswdshow),  # 忘记密码的表单展示
    url(r'^resetpwd.html', views.resetpasswd),  # 忘记密码的发送验证码、表单提交

    # 个人信息相关
    url(r'^logout$', views.logout, name="logout"),  # 注销
    url(r'^profile.html', views.profile),  # 个人信息查看
    url(r'^upload_avatar/', views.upload_avatar),  # 上传头像预览功能（第三种实现方式：Ajax保存到本地再传回html预览）
    url(r'(\w+)/editprofile.html', views.editprofile, name='editprofile'),  # 个人信息保存
    url(r'^editpwd.html', views.editpwd),  # 发送邮件验证码、表单提交

    # 管理员相关
    url(r'^manageadmin.html', views.manageadmin, name='manad'),  # 管理员信息页面
    url(r'^addadmininfo', views.addadmininfo),  # 添加管理员
    url(r'^editadmininfo', views.editadmininfo),  # 编辑管理员的表单提交
    url(r'(\w+)/deladmininfo.html', views.deladmininfo, name="deladmin"),  # 删除已经存在的管理员
    url(r'^authmanege.html', views.manageauth, name='manauth'),  # 权限管理信息展示、表单接收

    # 爬虫管理
    url(r'^spidercom.html', views.spidercom, name="spicom"),  # 商品爬取设置页面
    url(r'dosearch', views.dosearch, name="search"),  # 商品爬取GET请求、POST保存
    url(r'^recommond.html$', views.recommond, name="recommond"),  # 推荐商品爬取设置页面
    url(r'dorecommond', views.dorecommond),  # 推荐商品爬取GET请求、POST保存

    # 数据管理相关
    url(r'^allcommondity.html', views.allcominfo, name="commondityinfo"),  # 数据库里所有的商品信息
    url(r'delcom', views.delcommondity, name="delcom"),  # 删除商品
    url(r'^priceinfo.html', views.priceinfo, name="priceinfo"),  # 所有的价格信息
    url(r'delprice', views.delprice, name="delprice"),  # 删除价格
    url(r'^recom_info.html', views.recom_info, name="recom_info"),  # 推荐商品信息
    url(r'delrecom', views.delrecom, name="delrecom"),  # 删除推荐商品
]
