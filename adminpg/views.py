import time
import datetime
import json
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# 词云
import jieba
import numpy as np
import PIL.Image as image
from wordcloud import WordCloud
# 邮件
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
# 爬虫
import requests
from bs4 import BeautifulSoup

from adminpg import models
from sql import sqlhelper

sqlhelper = sqlhelper.SQLHELPER()

# 全局变量
salt = None
authid = None


# 验证是否登录    美/ˈverɪfaɪ/  核实，查证
def verify(request):
    cookies = request.COOKIES
    uid = cookies.get('uid')
    authority = cookies.get('authority')
    if uid is not None and authority is not None:
        # print("登录验证通过")
        return True
    else:
        print("登录验证未通过")
        return False


# 新增商品的数量
def renew_com_num():
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    before = now - delta
    comnum = sqlhelper.get_one(
        "select count(price) from adminpg_price_info WHERE dates>=%s AND dates<=%s", [before, now])
    return comnum[0]


# 新增 商品、推荐商品、价格、管理员 的数量
def renewsysinfo():
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    before = now - delta
    renewcom = sqlhelper.get_one(
        "select count(price) from adminpg_price_info WHERE dates>=%s AND dates<=%s", [before, now])
    renewrecom = sqlhelper.get_one(
        "select count(recom_id) from adminpg_recommend WHERE recom_date>=%s AND recom_date<=%s", [before, now])
    # renewprice = sqlhelper.get_one(
    #     "select count(price_com_id_id) from adminpg_pricecompare WHERE date>=%s AND date<=%s", [before, now])
    addmanager = sqlhelper.get_one(
        "select count(id) from adminpg_admin_info WHERE register_data>=%s AND register_data<=%s", [before, now])
    return [(renewcom[0], renewrecom[0], renewcom[0], addmanager[0])]


# 商品名称的词云图制作
def com_wordcloud():
    filename = 'static\wordcloud\com_wordcloud.txt'
    with open(filename, 'w', encoding="utf-8") as f:
        comall = sqlhelper.get_list('select com_name from adminpg_commodity_info WHERE 1=%s', 1)
        for i in comall:
            f.write(i[0])
        print("商品词云txt写入完毕")
    with open(filename, 'r', encoding="utf-8") as openfile:
        text = openfile.read()
        word_list = jieba.cut(text)
        result = " ".join(word_list)
        imgname = 'static\wordcloud\jd.jpg'
        mask = np.array(image.open(imgname))
        wordcloud = WordCloud(
            mask=mask,
            contour_width=5,
            # height=400,  # 当设置了背景的img时这是长宽将被忽略
            # width=500,
            min_font_size=10,
            max_font_size=90,
            background_color="white",
            # mode='RGBA',
            # colormap="viridis",  # 给每个字体随机分配颜色
            contour_color="White",
            random_state=30,  # 30中生成颜色
            font_path="../static/fonts/simsun.ttc"
            # font_path="C:\\Windows\\Fonts\\STXIHEI.TTF"
        ).generate(result)
        # image_produce = wordcloud.to_image()
        # image_produce.show()
        wordcloud.to_file("static\wordcloud\product.jpg")
        print("商品词云jpg制作完成")


# 推荐商品的词云图制作
def recom_wordcloud():
    filename = "static\wordcloud\jian_wordcloud.txt"
    with open(filename, 'w', encoding="utf-8") as f:
        comall = sqlhelper.get_list('SELECT recom_title from adminpg_recommend where 1=%s', 1)
        for i in comall:
            f.write(i[0])
        print("推荐商品词云txt写入完毕")
    with open(filename, 'r', encoding="utf-8") as openfile:
        text = openfile.read()
        word_list = jieba.cut(text)
        result = " ".join(word_list)
        imgname = "static\wordcloud\jianrecom.jpg"
        mask = np.array(image.open(imgname))
        wordcloud = WordCloud(
            mask=mask,
            contour_width=5,
            min_font_size=10,
            max_font_size=90,
            background_color="white",
            contour_color="White",
            random_state=40,  # 30中生成颜色
            # font_path="C:\\Windows\\Fonts\\STXIHEI.TTF"
            font_path="../static/fonts/simsun.ttc"
        ).generate(result)
        image_produce = wordcloud.to_image()
        wordcloud.to_file("static\wordcloud\jian_product.jpg")
        print("推荐商品词云jpg制作完成")


# 一开始的主页
def index(request):
    if request.method == "GET":
        if verify(request):
            com_wordcloud()
            recom_wordcloud()
            uid = request.COOKIES.get('uid')
            info = models.admin_info.objects.all().filter(id=uid).first()
            commun = models.commodity_info.objects.all().count()
            recomnum = models.recommend.objects.all().count()
            pricenum = models.commodity_info.objects.all().count()
            managenum = models.admin_info.objects.all().count()
            return render(request, 'admin/index.html',
                          {'admininfo': info, "info": [(commun, recomnum, pricenum, managenum)],
                           "renew": renew_com_num(), 'numinfo': renewsysinfo()})
        else:
            return redirect('/admin/login.html')
    else:
        return redirect('/admin/login.html')


# 母版布局页面
def layout(request):
    uid = '1002'
    info = models.admin_info.objects.all().filter(id=uid).first()
    return render(request, 'admin/layout.html', {'admininfo': info})


# 登陆页面
def login(request):
    if request.method == 'GET':
        return render(request, 'admin/login.html')
    global authid, id1
    ret = {'status': True, 'message': None}
    if request.method == "POST":
        try:
            id1 = request.POST.get('id')
            pwd = request.POST.get('pwd')
            if len(id1) > 0 and len(pwd) > 0:
                result = models.admin_info.objects.filter(id=id1).filter(pwd=pwd).count()
                if result == 1:
                    ret['status'] = True
                    obj = HttpResponse(json.dumps(ret))
                    authid = sqlhelper.get_one("select authority_fk_id from adminpg_admin_info where id=%s",
                                               [id1, ])
                    # 设置ticket的值  生效时长3天
                    obj.set_cookie('uid', id1, max_age=60 * 60 * 24 * 3)
                    obj.set_cookie('authority', authid[0], max_age=60 * 60 * 24 * 3)
                    return obj
                else:
                    ret['status'] = False
                    ret['message'] = '输入的账号或者密码有误！！'
            else:
                ret['status'] = False
                ret['message'] = '输入的账号或者密码不能为空！！'
        except Exception as e:
            ret['status'] = False
        obj = HttpResponse(json.dumps(ret))
        return obj


# 忘记密码表单展示
def resetpasswdshow(request):
    if request.method == 'GET':
        return render(request, 'admin/resetpasswd.html')


# 被调用的 发邮件功能
def mail(username, useremail, salt):
    my_sender = 'example@qq.com'  # 发件人邮箱账号
    my_pass = 'example'  # 发件人邮箱密码
    my_user = useremail
    ret = True
    try:
        msg = MIMEText('{name}您好！为确保是您本人操作，请在邮件验证码输入框输入下方验证码：{passwd}'.format(
            name=username, passwd=salt), 'plain', 'utf-8')
        msg['From'] = formataddr(("在线购物比价搜索引擎管理员", my_sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(("customer", my_user))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "搜索引擎管理系统密码重置"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    if ret:
        print("邮件发送成功")
        return True
    else:
        print("邮件发送失败")
        return False


# def runsendemail():
#     string = str(time.time() * 7).split('.', 1)
#     salt = string[1]  # 邮箱的验证码
#     mail('example', 'example@qq.com', salt)


# 忘记密码的发送验证码、表单提交
def resetpasswd(request):
    global salt
    ret = {'status': True, 'message': ""}
    if request.is_ajax():
        if request.method == "GET":
            try:
                uid = request.GET.get('id')
                uemail = request.GET.get('email')
                result = models.admin_info.objects.filter(id=uid).filter(email=uemail).count()
                if result == 1:
                    result = sqlhelper.get_one("select name from adminpg_admin_info where id=%s", [uid])
                    username = result[0]
                    ret['status'] = True
                    string = str(time.time() * 7).split('.', 1)  # 验证码
                    salt = string[1]
                    mailstatus = mail(username, uemail, salt)
                    if mailstatus:
                        ret['message'] = "验证码发送成功"
                    else:
                        ret['message'] = "请稍候重试！"
                else:
                    ret['status'] = False
                    ret['message'] = '您输入的数据有误！'
            except Exception as e:
                ret['status'] = False
        if request.method == "POST":
            try:
                uid = request.POST.get('id')
                sendsalt = request.POST.get('salt')
                if sendsalt == salt:
                    newpwd = request.POST.get('pwd')
                    newpwdrep = request.POST.get('pwdrep')
                    if newpwd == newpwdrep:
                        models.admin_info.objects.filter(id=uid).update(pwd=newpwd)
                        ret['status'] = True
                        ret['message'] = "修改成功"
                    else:
                        ret['status'] = False
                        ret['message'] = "两次输入的密码不一致！"
                else:
                    ret['status'] = False
                    ret['message'] = "输入的验证码有误，请核对！"
            except Exception as e:
                ret['status'] = False
    return HttpResponse(json.dumps(ret))


# 退出页面
def logout(request):
    response = redirect('login')
    response.delete_cookie('uid')
    response.delete_cookie('authority')
    return response


# 显示个人信息页面
def profile(request):
    if verify(request):
        # print("优化后的profile")
        uid = request.COOKIES.get('uid')
        info = models.admin_info.objects.all().filter(id=uid).first()
        num = renew_com_num()
        return render(request, 'admin/profile.html', {'admininfo': info, 'renew': num})
    else:
        return redirect('admin/login.html')


# 上传头像显示预览
def upload_avatar(request):
    file_obj = request.FILES.get('avatar')
    file_path = os.path.join('static/images', file_obj.name)
    print(file_path)
    with open(file_path, 'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    return HttpResponse(file_path)


# 个人信息修改后保存
def editprofile(request, uid):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        result = request.FILES.get('img')
        if result is not None:
            filesize = request.FILES.get('img').size
            print("上传的图片的大小", filesize)
            # 把文件上传到本地保存
            if filesize <= 1050000:
                avatarname = request.FILES.get('img').name
                admin = models.admin_info.objects.get(id=uid)
                admin.avatar = request.FILES['img']
                admin.save()
                models.admin_info.objects.filter(id=uid).update(name=name, email=email, avatarname=avatarname)
                return redirect('/admin/profile.html')
            else:
                return redirect('/admin/profile.html')
        else:
            # 用户未修改头像
            models.admin_info.objects.filter(id=uid).update(name=name, email=email, )
            return redirect('/admin/profile.html')


# 发邮件验证码、表单提交
def editpwd(request):
    global salt
    ret = {'status': True, 'message': ""}
    if request.method == "GET":
        try:
            uemail = request.GET.get('email')
            uname = request.GET.get('uname')
            string = str(time.time() * 7).split('.', 1)  # 验证码
            salt = string[1]
            mailstatus = mail(uname, uemail, salt)
            if mailstatus:
                ret['status'] = True
                ret['message'] = "验证码发送成功"
            else:
                ret['status'] = False
                ret['message'] = "发送失败,请稍候重试！"
        except Exception as e:
            ret['status'] = False
        return HttpResponse(json.dumps(ret))
    # post提交数据
    if request.method == "POST":
        try:
            uid = request.POST.get('id')
            sendsalt = request.POST.get('salt')
            oldpwd = request.POST.get('oldpwd')
            newpwd = request.POST.get('newpwd')
            newpwdrep = request.POST.get('newpwdrep')
            result = models.admin_info.objects.filter(id=uid).filter(pwd=oldpwd).count()
            if result == 1:
                if sendsalt == salt:
                    if newpwd == newpwdrep:
                        # 全部验证通过  修改数据
                        models.admin_info.objects.filter(id=uid).update(pwd=newpwd)
                        ret['status'] = True
                        ret['message'] = "修改成功"
                    else:
                        ret['status'] = False
                        ret['message'] = "两次输入的密码不一致！"
                else:
                    ret['status'] = False
                    ret['message'] = "输入的验证码有误，请核对！"
            else:
                ret['status'] = False
                ret['message'] = "原密码有误！"
        except Exception as e:
            ret['status'] = False
        return HttpResponse(json.dumps(ret))


# 管理员信息
def manageadmin(request):
    if request.method == "GET":
        if verify(request):
            uid = request.COOKIES.get('uid')
            info = models.admin_info.objects.all().filter(id=uid).first()
            infolist = models.admin_info.objects.all()
            auth = models.authority_info.objects.all()
            num = renew_com_num()
            return render(request, 'admin/manageadmin.html',
                          {'admininfo': info, 'infolist': infolist, 'auth': auth, 'renew': num})


# 添加管理员
def addadmininfo(request):
    ret = {'status': True, 'message': ""}
    if request.method == "POST":
        if verify(request):
            id = request.POST.get('id')
            name = request.POST.get('name')
            pwd = request.POST.get('pwd')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            auth = request.POST.get('auth')
            file_obj = request.FILES.get('avatar')
            registtime = datetime.datetime.now()
            print(id, name, pwd, email, phone, auth, registtime)
            result = models.admin_info.objects.filter(id=id).count()
            print("id主键:", id, result)
            if len(id) is None or len(name) is None or len(pwd) is None or len(phone) is None or len(email) is None:
                ret['status'] = False
                ret['message'] = "不能为空"
                print("不能为空")
            elif result == 1:
                ret['status'] = False
                ret['message'] = "id为主键值，不能重复！"
                print("id为主键值，不能重复！")
            else:
                try:
                    filesize = file_obj.size
                    print("addadmin上传的图片的大小", filesize)
                    # 把文件上传到本地保存
                    if filesize < 1050000:
                        avatarname = file_obj.name
                        models.admin_info.objects.create(id=id, pwd=pwd, name=name, avatarname=avatarname, phone=phone,
                                                         register_data=registtime, authority_fk_id=auth, email=email)
                        admin = models.admin_info.objects.get(id=id)
                        admin.avatar = file_obj
                        admin.save()
                        ret['message'] = "添加成功"
                        ret['status'] = True
                        print("添加成功")
                    else:
                        ret['status'] = False
                        ret['message'] = "图片太大，请上传小于1m的图片！"
                        print("图片太大，请上传小于1m的图片！")
                except Exception as e:
                    ret['status'] = False
            return HttpResponse(json.dumps(ret))


# 编辑管理员的表单提交
def editadmininfo(request):
    ret = {'status': True, 'message': ""}
    if request.method == "POST":
        print("这是post修改管理员信息")
        if verify(request):
            id = request.POST.get('id')
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            auth = request.POST.get('auth')
            file_obj = request.FILES.get('avatar')
            print(id, name, email, phone, auth)
            if file_obj is not None:
                try:
                    filesize = file_obj.size
                    print("修改管理员上传的图片的大小", filesize)
                    # 把文件上传到本地保存
                    if filesize < 1050000:
                        avatarname = file_obj.name
                        admin = models.admin_info.objects.get(id=id)
                        admin.avatar = file_obj
                        admin.save()
                        models.admin_info.objects.filter(id=id).update(name=name, avatarname=avatarname, phone=phone,
                                                                       authority_fk_id=auth, email=email)
                        ret['message'] = "修改成功"
                        ret['status'] = True
                        print("修改成功")
                    else:
                        ret['status'] = False
                        ret['message'] = "图片太大，请上传小于1m的图片！"
                        print("图片太大，请上传小于1m的图片！")
                except Exception as e:
                    ret['status'] = False
            else:
                # 修改信息时未修改图片
                models.admin_info.objects.filter(id=id).update(name=name, phone=phone, authority_fk_id=auth,
                                                               email=email)
                ret['message'] = "修改成功"
                ret['status'] = True
                print("修改成功")
            return HttpResponse(json.dumps(ret))


# 删除管理员
def deladmininfo(request, id):
    models.admin_info.objects.filter(id=id).delete()
    return redirect('/admin/manageadmin.html')


# 权限管理信息展示、表单接收
def manageauth(request):
    if request.method == "GET":
        print("这是查看管理员的权限信息")
        if verify(request):
            adminlist = models.admin_info.objects.all()
            authinfo = models.authority_info.objects.all()
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            num = renew_com_num()
            return render(request, 'admin/authmanager.html',
                          {'admininfo': admininfo, 'infolist': adminlist, 'authinfo': authinfo, 'renew': num})
    if request.method == "POST":
        print("修改管理员的权限信息")
        name = request.POST.get('adminname')
        auth = request.POST.get('authid')
        authid = models.authority_info.objects.filter(describe=auth).first()
        print("name:", name, "权限编号：", authid.authority)
        authid = authid.authority
        models.admin_info.objects.filter(name=name).update(authority_fk_id=authid)
        print("修改成功！！")
        return redirect('authmanege.html')


# 商品爬取设置页面
def spidercom(request):
    if request.method == "GET":
        print("商品爬虫的管理页面")
        if verify(request):
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            num = renew_com_num()
            return render(request, 'admin/spider_commondity.html',
                          {'admininfo': admininfo, 'renew': num})


cargoods = []
jdcom = []


# 爬取京东
def spider_jd(type, keys, num):
    if type == 'search':
        print("这是京东的搜索！！")
        re = requests.get(
            url="https://search.jd.com/Search?keyword=" + keys + "&enc=utf-8&",
            headers={
                'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac 05 X 10_11_4)AppleWebKit/537.36(KHTML,like Gecko)'
                              'Chrome/52.0.2743.116 Safari/537.36'
            })
        re.encoding = 'utf-8'
        soup = BeautifulSoup(re.text, 'html.parser')
        li = soup.find(attrs={'class': 'gl-warp clearfix'}).find_all(attrs={'class': "gl-item"})
        flag = 0
        global jdcom
        global jdprice
        if flag < int(num):
            for list in li:
                imgattrs = list.find(name='div').find(attrs={'class': "p-img"}).select("a img")
                imgsrc = imgattrs[0].get('src')

                a = list.find(class_="p-name").select("a")
                url = a[0].get('href')

                em = list.find(class_="p-name").select("a em")
                title = em[0].text

                iprice = list.find(class_="p-price").select("strong i")
                price = iprice[0].text

                acomment = list.find(class_="p-commit").select("strong a")
                deal = acomment[0].text

                ashop = list.find(class_="p-shop").select("span a")
                if ashop:
                    shop = ashop[0].get('title')
                else:
                    shop = " "
                location = "京东搜索"
                temp = (url, title, imgsrc, shop, price, deal, location)
                jdcom.append(temp)
                flag = flag + 1
                if flag >= int(num):
                    break
        print(jdcom)


tbcars = []
tbcom = []


# 爬取淘宝天猫
def spider_taobao(type, keys, num):
    global tbcom
    if type == "search":
        print("这是淘宝的搜索！！")
        re = requests.get(
            url="https://list.tmall.com/search_product.htm?q=" +
                keys + "&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton",
            headers={
                'Accept': '*/*',
                'Accept-Language': 'zh-CN',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
            },
        )
        soup = BeautifulSoup(re.text, 'lxml')
        li = soup.find_all(attrs={'class': "product"})
        flag = 0
        if flag < int(num):
            for item in li:
                href = item.find(class_="productImg-wrap").select("a")[0].get('href')
                imgurl = item.find(class_="productImg-wrap").select("a img")[0].get('src')
                title = item.find(class_="productTitle").select("a")[0].get('title')
                price = item.find(class_="productPrice").select("em")[0].get('title')
                shop = item.find(class_="productShop").select("a")[0].text.replace(" ", "").replace("\n", "").replace(
                    "\r", "")
                deal = item.find(class_="productStatus").select("span em")[0].text.replace(" ", "").replace(
                    "\n", "").replace("\r", "")
                location = "天猫商城"
                temp = (href, title, imgurl, shop, price, deal, location)
                tbcom.append(temp)
                flag = flag + 1
                if flag >= int(num):
                    break
    print(tbcom)


sncom = []
sncars = []


# 爬取苏宁
def spider_suning(type, key, num):
    if type == "search":
        print("这是苏宁的搜索！！")
        re = requests.get(
            url="https://search.suning.com/" + key + "/",
            headers={
                'Accept': '*/*',
                'Accept-Language': 'zh-CN',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/81.0.4044.92 Safari/537.36'
            },
        )
        re.encoding = 'utf-8'
        soup = BeautifulSoup(re.text, 'html.parser')
        li = soup.find(class_="general clearfix").find_all(attrs={'doctype': "1"})
        flag = 0
        global sncom
        if flag < int(num):
            for list in li:
                img = list.find(class_="product-box").select("div div a img")
                imgurl = img[0].get("src")

                url = list.find(class_="product-box").find(name='div', class_="title-selling-point").select("a")
                href = url[0].get("href")

                name = list.find(class_="product-box").find(name='div', class_="title-selling-point").select("a")
                title = name[0].text

                # sprice=list.find(name='div',class_="price-box").select("span")
                # price=sprice[0].text
                # print(sprice)
                price = None

                eval = list.find(name='div', class_="info-evaluate").select("a i")
                if eval:
                    deal = eval[0].text
                else:
                    continue

                ashop = list.find(name='div', class_="store-stock").select("a")
                shop = ashop[0].text

                location = "苏宁搜索"
                price = ""
                temp = (href, title, imgurl, shop, price, deal, location)
                sncom.append(temp)
                flag = flag + 1
                if flag >= int(num):
                    break
        print(sncom)


# 商品爬取GET请求、POST保存
def dosearch(request):
    ret = {'status': True, 'message': "", 'insertnum': "", 'jd': "", 'tb': "", 'sn': ""}
    global jdcom
    global sncom
    global tbcom
    if request.method == "GET":
        print("这是提交商品爬虫查询的处理")
        jdstatus = request.GET.get('jd')
        jdnum = request.GET.get('jdnum')
        tbstatus = request.GET.get('tb')
        tbnum = request.GET.get('tbnum')
        snstatus = request.GET.get('sn')
        snnum = request.GET.get('snnum')
        setext = request.GET.get('setext')
        print("数据状态：", jdstatus, jdnum, tbstatus, tbnum, snstatus, snnum, setext)
        status = "search"
        # 在开始搜索的时候要让之前的数据清空
        jdcom = []
        sncom = []
        tbcom = []
        try:
            if jdstatus == "true":
                spider_jd(status, setext, jdnum)
                ret['jd'] = jdcom
            if tbstatus == "true":
                spider_taobao(status, setext, tbnum)
                ret['tb'] = tbcom
            if snstatus == "true":
                spider_suning(status, setext, snnum)
                ret['sn'] = sncom
        except Exception as e:
            ret['message'] = "没有合适的输入条件"
            ret['status'] = False
        return HttpResponse(json.dumps(ret))

    if request.method == "POST":
        print("这是mysql保存刚才爬取的数据！")
        com_info = []
        priceinfo = []
        nowprice = []
        createdate = str(datetime.datetime.now())
        if jdcom is not None:
            for i in jdcom:
                temp = (i[0], i[1], i[2], i[3], i[5], i[6])
                com_info.append(temp)
                temp1 = (createdate, i[4], i[0])
                priceinfo.append(temp1)
                temp3 = [i[4]]
                nowprice.append(temp3)
        if sncom is not None:
            for i in sncom:
                temp = (i[0], i[1], i[2], i[3], i[5], i[6])
                com_info.append(temp)
                temp1 = (createdate, i[4], i[0])
                priceinfo.append(temp1)
                temp3 = [i[4]]
                nowprice.append(temp3)
        if tbcom is not None:
            for i in tbcom:
                temp = (i[0], i[1], i[2], i[3], i[5], i[6])
                com_info.append(temp)
                temp1 = (createdate, i[4], i[0])
                priceinfo.append(temp1)
                temp3 = [i[4]]
                nowprice.append(temp3)
        # replace...  当主键冲突时将直接替换，不会报错
        sqlhelper.multiple_modify("replace into adminpg_commodity_info values(%s,%s,%s,%s,%s,%s)", com_info)
        sqlhelper.multiple_modify('insert into adminpg_price_info(dates,price,com_fk_id) values(%s,%s,%s)', priceinfo)
        # models.price_info.objects.bulk_create(priceinfo)
        ret['status'] = True
        ret['message'] = "保存数据成功！！"
        num = models.price_info.objects.filter(dates=createdate).count()
        ret['insertnum'] = num
        return HttpResponse(json.dumps(ret))


# 推荐商品爬取设置页面
def recommond(request):
    if request.method == "GET":
        print("推荐商品爬取设置页面")
        if verify(request):
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            num = renew_com_num()
            return render(request, 'admin/recommond.html',
                          {'admininfo': admininfo, 'renew': num})


def shorturl(orurl):
    url = "http://shorturl.8446666.sojson.com/sina/shorturl?url=" + orurl
    re = requests.get(url)
    if re.status_code == 200:
        jsontext = json.loads(re.text)
        shortulr = jsontext["shorturl"]
        return shortulr
    else:
        print("短链接生成失败")
        return orurl


hiscom = []


# 搜索历史低价推荐商品
def spider_his(num):
    res = requests.get(
        url='https://www.gwdang.com/promotion/price',
        headers={'Host': 'hm.baidu.com',
                 'Connection': 'keep-alive',
                 'Referer': 'https://www.gwdang.com/promotion/price',
                 'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac 05 X 10_11_4)AppleWebKit/'
                               '537.36(KHTML,like Gecko)Chrome/52.0.2743.116 Safari/537.36'})
    soup = BeautifulSoup(res.text, 'html.parser')
    list = soup.find_all(name="li", class_="zdm_li pos_r")
    global hiscom
    flag = 0
    if flag < int(num):
        for item in list:
            img = item.find(name="div", class_="section-1").select("a img")[0]
            imgurl = img.get("data-original")

            title = item.find(name="div", class_="section-2").select("div a")[0].get("title")

            price = item.find(name="div", class_="section-2").find(name="span", class_="price").text

            shop = item.find(name="div", class_="site-info pos_a").find(name="span", class_="site-name").text

            str = item.find(name="a", class_="btn btn-buy pos_a").get("href")
            if str.startswith('/union/go'):
                href = "https://www.gwdang.com/" + str
            else:
                href = str

            if len(href) > 250:
                href = shorturl(href)

            temp = (href, title, imgurl, price, shop)
            hiscom.append(temp)
            flag = flag + 1
            if flag >= int(num):
                break
    print(hiscom)


jxcom = []


# 搜索精选推荐商品
def spider_jx(num):
    res = requests.get(
        url='https://www.gwdang.com/promotion/zhi',
        headers={
            'method': 'GET',
            'scheme': 'https',
            'cookie': 'index_big_banner=1; GWD_ACCESS_TOKEN=0d835edb16f1ed224190dc5f244c21dd; '
                      'Hm_lvt_7705e8554135f4d7b42e62562322b3ad=1588854487,1588855067,1588855825,1588866582; '
                      'fp=0a4d4089b2a140351864124a079476e2; '
                      '__utma=188916852.1560941891.1587714303.1588854495.1588866582.4; '
                      '__utmc=188916852; __utmz=188916852.1588866582.4.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic;'
                      ' __utmt=1; __utmb=188916852.4.10.1588866582; '
                      'Hm_lpvt_7705e8554135f4d7b42e62562322b3ad=1588867151; '
                      'dfp=0H88kUZeEH88kUZM0H88kUZM0CM2kUZM0W88EVZM0H820UZM0UM=EUZ86Ut80c55',
            'path': '/promotion/zhi',
            'authority': 'www.gwdang.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.72 Safari/537.36'})
    soup = BeautifulSoup(res.text, 'html.parser')
    list = soup.find_all(name="li", class_="zdm_li pos_r")
    # print(list)
    global jxcom
    flag = 0
    if flag < int(num):
        for item in list:
            img = item.find(name="div", class_="section-1").select("a img")[0]
            imgurl = img.get("data-original")
            title = item.find(name="div", class_="section-2").select("div a")[0].get("title")
            price = item.find(name="div", class_="section-2").find(name="span", class_="price").text
            shop = item.find(name="div", class_="site-info pos_a").find(name="span", class_="site-name").text
            str = item.find(name="a", isconvert="0", class_="btn btn-buy pos_a").get("href")
            if str.startswith('/union/go'):
                href = "https://www.gwdang.com/" + str
            else:
                href = str
            if len(href) > 250:
                href = shorturl(href)
            temp = (href, title, imgurl, price, shop)
            jxcom.append(temp)
            flag = flag + 1
            if flag >= int(num):
                break
    print(jxcom)


yhcom = []


# 搜索优惠推荐商品
def spider_yh(num):
    import re
    res = requests.get(
        url='http://www.zdzdm.com/youhui',
        headers={
            'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac 05 X 10_11_4)AppleWebKit/537.36(KHTML,like Gecko)'
                          'Chrome/52.0.2743.116 Safari/537.36'})
    soup = BeautifulSoup(res.text, 'html.parser')
    list = soup.find_all(name="div", class_="new_info_list")
    global yhcom
    flag = 0
    if flag < int(num):
        for item in list:
            ahref = item.find(name="a", target="_blank")
            href = ahref.get("href")
            title = ahref.get("title")

            spanprice = item.find(name="a", target="_blank").select("span")[0].text.replace(" ", "").replace('\n',
                                                                                                             "").replace(
                '\r', "")
            price = re.search('([1-9].*)元', spanprice)[0]

            img = item.find(name="div", class_="zdm_img").select("a img")
            imgurl = img[0].get("src")

            ddescribe = item.find(name="div", class_="list_txt").select("p")[0].text.replace(" ", "").replace('\n',
                                                                                                              "").replace(
                '\r', "")
            desc = ddescribe[0:45]
            if len(href) > 250:
                href = shorturl(href)

            temp = (href, title, imgurl, price, desc)
            yhcom.append(temp)
            flag = flag + 1
            if flag >= int(num):
                break
    print(yhcom)


# 推荐商品爬取GET请求、POST保存
def dorecommond(request):
    ret = {'status': True, 'message': "", 'insertnum': "", 'his': "", 'jx': "", 'yh': ""}
    global hiscom
    global yhcom
    global jxcom
    if request.method == "GET":
        print("这是提交推荐商品爬虫的处理")
        hisstatus = request.GET.get('his')
        hisnum = request.GET.get('hisnum')
        jxstatus = request.GET.get('jx')
        jxnum = request.GET.get('jxnum')
        yhstatus = request.GET.get('yh')
        yhnum = request.GET.get('yhnum')
        print("推荐商品爬虫的数据状态：", hisstatus, hisnum, jxstatus, jxnum, yhstatus, yhnum)
        # 在开始搜索的时候要让之前的数据清空
        hiscom = []
        jxcom = []
        yhcom = []
        try:
            if hisstatus == "true":
                spider_his(hisnum)
                ret['his'] = hiscom
            if jxstatus == "true":
                spider_jx(jxnum)
                ret['jx'] = jxcom
            if yhstatus == "true":
                spider_yh(yhnum)
                ret['yh'] = yhcom
        except Exception as e:
            ret['status'] = False
            ret['message'] = "输入条件有误"
        return HttpResponse(json.dumps(ret))
    if request.method == "POST":
        print("这是mysql保存刚才爬取的推荐数据！")
        recommond_com = []
        createdate = datetime.datetime.now()
        if hiscom is not None:
            for i in hiscom:
                temp1 = (i[0], i[1], i[2], i[3], i[4], createdate)
                recommond_com.append(temp1)
        if jxcom is not None:
            for i in jxcom:
                temp2 = (i[0], i[1], i[2], i[3], i[4], createdate)
                recommond_com.append(temp2)
        if yhcom is not None:
            for i in yhcom:
                temp3 = (i[0], i[1], i[2], i[3], i[4], createdate)
                recommond_com.append(temp3)
        sqlhelper.multiple_modify("replace into adminpg_recommend values(%s,%s,%s,%s,%s,%s)", recommond_com)
        # sqlhelper.close()
        ret['status'] = True
        ret['message'] = "保存数据成功！！"
        num = models.recommend.objects.filter(recom_date=createdate).count()
        ret['insertnum'] = num
        return HttpResponse(json.dumps(ret))


# 数据库里所有的商品信息
def allcominfo(request):
    global currentpage1
    if request.method == "GET":
        print("所有商品信息页面")
        if verify(request):
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            comlist = models.commodity_info.objects.all()
            paginator = Paginator(comlist, 6)
            try:
                currentpage1 = request.GET.get('p')
                posts = paginator.page(currentpage1)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(1)
            if paginator.num_pages > 11:
                if int(currentpage1) - 5 < 1:
                    pagerange = range(1, 11)
                elif int(currentpage1) + 5 > int(paginator.num_pages):
                    pagerange = range(int(currentpage1) - 5, int(currentpage1) + 1)
                else:
                    pagerange = range(int(currentpage1) - 5, int(currentpage1) + 6)
            else:
                pagerange = paginator.page_range
            num = renew_com_num()
            return render(request, 'admin/allcommondity.html',
                          {'admininfo': admininfo, 'comlist': posts, 'pagerange': pagerange, 'renew': num})


# 删除商品
def delcommondity(request):
    if request.method == "POST":
        ret = {'status': True, 'message': None}
        url = request.POST.get("url")
        print("post删除商品信息：", url)
        try:
            models.commodity_info.objects.filter(com_id=url).delete()
            ret["message"] = "删除成功"
            ret["status"] = True
        except Exception as e:
            ret["message"] = "删除出错"
            ret["status"] = False
        return HttpResponse(json.dumps(ret))


# 价格信息
def priceinfo(request):
    global currentpage2
    if request.method == "GET":
        print("所有的商品价格信息")
        if verify(request):
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            comlist = models.commodity_info.objects.all()
            paginator = Paginator(comlist, 6)
            try:
                currentpage2 = request.GET.get('p')
                posts = paginator.page(currentpage2)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(1)
            if paginator.num_pages > 11:
                pass
                if int(currentpage2) - 5 < 1:
                    pagerange = range(1, 11)
                elif int(currentpage2) + 5 > int(paginator.num_pages):
                    pagerange = range(int(currentpage2) - 5, int(currentpage2) + 1)
                else:
                    pagerange = range(int(currentpage2) - 5, int(currentpage2) + 6)
            else:
                pagerange = paginator.page_range
            num = renew_com_num()
            return render(request, 'admin/priceinfo.html',
                          {'admininfo': admininfo, 'comlist': posts, 'pagerange': pagerange, 'renew': num})


# 删除价格
def delprice(request):
    if request.method == "POST":
        ret = {'status': True, 'message': None}
        url = request.POST.get("url")
        print("post删除价格信息：", url)
        try:
            models.commodity_info.objects.filter(com_id=url).delete()
            ret["message"] = "删除成功"
            ret["status"] = True
        except Exception as e:
            ret["message"] = "删除出错"
            ret["status"] = False
        return HttpResponse(json.dumps(ret))


# 所有推荐商品
def recom_info(request):
    global currentpage3
    if request.method == "GET":
        print("所有的推荐商品信息")
        if verify(request):
            uid = request.COOKIES.get('uid')
            admininfo = models.admin_info.objects.all().filter(id=uid).first()
            comlist = models.recommend.objects.all().order_by("-recom_date")
            paginator = Paginator(comlist, 6)
            try:
                currentpage3 = request.GET.get('p')
                posts = paginator.page(currentpage3)
            except PageNotAnInteger:
                posts = paginator.page(1)
                # posts = range(1)
            except EmptyPage:
                posts = paginator.page(1)
            if paginator.num_pages > 6:
                pass
                if int(currentpage3) - 5 < 1:
                    pagerange = range(1, 6)
                elif int(currentpage3) + 5 > int(paginator.num_pages):
                    pagerange = range(int(currentpage3) - 5, int(currentpage3) + 1)
                else:
                    pagerange = range(int(currentpage3) - 5, int(currentpage3) + 6)
            else:
                pagerange = paginator.page_range
            num = renew_com_num()
            return render(request, 'admin/recom_info.html',
                          {'admininfo': admininfo, 'comlist': posts, 'pagerange': pagerange, 'renew': num})


# 删除推荐商品
def delrecom(request):
    ret = {'status': True, 'message': None}
    if request.method == "POST":
        comid = request.POST.get("url")
        print("删除的recomid", comid)
        try:
            models.recommend.objects.filter(recom_id=comid).delete()
            ret["message"] = "删除成功"
            ret["status"] = True
        except Exception as e:
            ret["message"] = "删除出错"
            ret["status"] = False
    return HttpResponse(json.dumps(ret))
