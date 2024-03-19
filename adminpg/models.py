import os
from uuid import uuid4
from django.db import models


def path_and_rename(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid4().hex, ext)
    upload_to = 'avatars'
    return os.path.join(upload_to, filename)


# 权限信息表
class authority_info(models.Model):
    # objects = models.Manager
    authority = models.IntegerField(primary_key=True)
    describe = models.CharField(max_length=15)


# 管理人员的信息表
class admin_info(models.Model):
    # objects = models.Manager
    id = models.CharField(primary_key=True, max_length=32)
    pwd = models.CharField(max_length=32)
    name = models.CharField(max_length=16)
    email = models.EmailField(default='example.@email.com')
    avatar = models.ImageField(upload_to=path_and_rename, null=True)
    avatarname = models.CharField(max_length=64)
    phone = models.CharField(max_length=11)
    register_data = models.DateTimeField()
    authority_fk = models.ForeignKey("authority_info", on_delete=models.CASCADE)


# 商品信息表
class commodity_info(models.Model):
    # objects = models.Manager
    com_id = models.CharField(primary_key=True, max_length=250)
    com_name = models.CharField(max_length=250)
    com_img = models.URLField(max_length=250, null=True)
    com_shop = models.CharField(max_length=30, null=True)
    com_evaluate = models.CharField(max_length=30, null=True)
    com_source = models.CharField(max_length=30)


# 价格信息表
class price_info(models.Model):
    # objects = models.Manager
    dates = models.DateTimeField()
    price = models.CharField(max_length=40, null=True)
    com_fk = models.ForeignKey("commodity_info", on_delete=models.CASCADE)


# 商品价格历史信息表
class pricecompare(models.Model):
    # objects = models.Manager
    max_price = models.CharField(max_length=15, null=True)
    max_date = models.DateTimeField()
    min_price = models.CharField(max_length=15, null=True)
    min_date = models.DateTimeField()
    price_com_id = models.ForeignKey("commodity_info", on_delete=models.CASCADE)


# 推荐商品信息表  美/ˌrekəˈmend/ 推荐
class recommend(models.Model):
    # objects = models.Manager
    recom_id = models.CharField(primary_key=True, max_length=250)
    recom_title = models.CharField(max_length=250)
    recom_img = models.CharField(max_length=250)
    recom_price = models.CharField(max_length=50, null=True)
    recom_desc = models.CharField(max_length=254)
    recom_date = models.DateTimeField()
