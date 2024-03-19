import json
import time
import sys
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render
from selenium.webdriver import Chrome

from adminpg import models
from sql import sqlhelper

sqlhelper = sqlhelper.SQLHELPER()


def dateparse(local):
    tuptime = time.localtime(local)
    standartime = time.strftime("%Y-%m-%d", tuptime)
    return standartime


def index(request):
    print("这是主页的访问")
    # 需要返回推荐的信息
    recom = models.recommend.objects.order_by("-recom_date")[:9]
    return render(request, 'customer/index.html', {"recommond": recom})


maxprice = None
maxdate = None
minprice = None
mindate = None
current = None


# 得到最高最低价格的地址然后搜索
def historypriceinfo(url):
    global maxdate
    global maxprice
    global mindate
    global minprice
    global current
    cookie_str = 'lsjgcxToken=6E50054E357C53F305D2DD93260D1BCAE6DE9A4207F3897BDB4271A51355CB813DD59AFB96FB13E7F06FA69B04013D34F711C37EF22A441DEC957D25C95F3BA3; lsjgcxToken=6E50054E357C53F305D2DD93260D1BCAE6DE9A4207F3897BDB4271A51355CB813DD59AFB96FB13E7F06FA69B04013D34F711C37EF22A441DEC957D25C95F3BA3; 69a1a_mmbuser=V09xQG5HOS0CeV15ZlB2WCQ2TUFdVlV1IUtFbTkAVlMFU1VVAABQBQ0HUgBTDAhQBgNVB1FXDl0AVw8IBTg%3d; auth_token=bggNSWl3Vi5%2bZwBwV2EBBDkIegpjcmkCNzN3UGZfZAZ5ZBciWmxfcG5cLiBkBWZlc3ZyYCE1CHBhVnpkJydZZXJUfGFyACU8fFQEcG5HWy9zYFcO; lsjgcx_userdev=%7b%22FirstDate%22%3a%222021-03-10+19%3a36%3a12%22%2c%22FirstLoginDate%22%3a%222021-04-07+20%3a03%3a17%22%2c%22LastLoginDate%22%3a%222021-05-26+22%3a21%3a06%22%2c%22DevNum%22%3a%22fabb923797f246e4a97f48520eec14ad%22%7d; Hm_lvt_72b68c351b528b0e3406619a64d8f8d0=1622036908,1622089600; ASP.NET_SessionId=0i5gr3iqquqf24szx2vcyqrs; Hm_lvt_01a310dc95b71311522403c3237671ae=1622038390,1622089654; Hm_lpvt_01a310dc95b71311522403c3237671ae=1622089654; ' \
                 'Hm_lpvt_72b68c351b528b0e3406619a64d8f8d0=1622089660'
    # 把cookie字符串处理成字典
    cookies = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
    res = requests.get(
        url='http://p.zwjhl.com/price.aspx?url=' + url, cookies=cookies, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.93 Safari/537.36'}
    )
    soup = BeautifulSoup(res.text, 'lxml')
    # print(soup)
    # print(soup.find(attrs={'class': 'bigwordprice'}))
    # print(soup.find(class_='title-item'))
    # print(soup.find_all(class_='bigwordprice'))
    print(url)

    # sys.exit(0)
    try:
        minprice = soup.find(attrs={'class': 'bigwordprice'}).text.replace('\n', '').replace(' ', '').replace('\r', '')
    except:
        minprice = None

    mindate = None

    try:
        current = soup.find(class_='title-item').text.replace('\n', '').replace('\r', '').replace(' ', '')[3:7]
    except Exception:
        current = None

    try:
        maxprice = soup.find_all(class_='bigwordprice')[1].text.replace('\n', '').replace(' ', '').replace('\r', '')
    except:
        maxprice = None
    maxdate = None

    # print(minprice, mindate, current, maxprice, maxdate)


jdcom = []
tianmaos = []
sncom = []
searchcom = []


def jdinfo(keys):
    print("这是京东购物的搜索！！")
    re = requests.get(
        url="https://search.jd.com/Search?keyword=" + keys + "&enc=utf-8&",
        headers={
            'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac 05 X 10_11_4)AppleWebKit/537.36(KHTML, '
                          'like Gecko)Chrome/52.0.2743.116 Safari/537.36'
        })
    re.encoding = 'utf-8'
    soup = BeautifulSoup(re.text, 'html.parser')
    li = soup.find(attrs={'class': 'gl-warp clearfix'}).find_all(attrs={'class': "gl-item"})
    flag = 1
    global jdcom
    shopname = None
    for list in li:
        shop = list.find(class_="p-shop").select("span a")[0].get('title')
        if flag > 3:
            break
        # 同一家店铺只保存一次
        if shopname != shop:
            shopname = shop

            imgattrs = list.find(name='div').find(attrs={'class': "p-img"}).select("img")
            imgsrc = imgattrs[0].get('data-lazy-img')

            a = list.find(class_="p-name").select("a")
            url = a[0].get('href')
            historypriceinfo(url)

            em = list.find(class_="p-name").select("a em")
            title = em[0].text

            iprice = list.find(class_="p-price").select("strong i")
            price = iprice[0].text

            deal = list.find(class_="p-commit").select("strong a")[0].text.replace('\n', '').replace(' ', '').replace(
                '\r', '')

            location = "京东搜索"
            temp = (imgsrc, url, title, price, maxprice, maxdate, minprice, mindate, deal, shop, location)
            jdcom.append(temp)
            flag = flag + 1
        else:
            continue
    # print(jdcom)


def tianmao(keys):
    print("这是天猫的搜索！！")
    re = requests.get(
        url="https://list.tmall.com/search_product.htm?q=" + keys +
            "&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton",
        headers={
            'Accept': '*/*',
            'Accept-Language': 'zh-CN',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/81.0.4044.92 Safari/537.36'
        },
    )
    soup = BeautifulSoup(re.text, 'lxml')
    li = soup.find_all(attrs={'class': "product"})
    global tianmaos
    flag = 1
    for item in li:
        suk = item.find(class_="productStatus").find(attrs={'data-icon': "small"}).get('data-item')
        # print(suk)
        suk = str(suk) + "-83"
        href = item.find(class_="productImg-wrap").select("a")[0].get('href')
        historypriceinfo(href)
        imgurl = item.find(class_="productImg-wrap").select("a img")[0].get('src')
        title = item.find(class_="productTitle").select("a")[0].get('title')
        price = item.find(class_="productPrice").select("em")[0].get('title')
        shop = item.find(class_="productShop").select("a")[0].text.replace(" ", "").replace("\n", "").replace("\r", "")
        deal = item.find(class_="productStatus").select("span em")[0].text.replace(" ", "").replace("\n", "").replace(
            "\r", "")
        location = "天猫商城"
        temp = (imgurl, href, title, price, maxprice, maxdate, minprice, mindate, deal, shop, location)
        tianmaos.append(temp)
        flag = flag + 1
        if flag > 3:
            break
    # print(tianmaos)


def suning(keys):
    print("这是苏宁的搜索！！")
    re = requests.get(
        url="https://search.suning.com/" + keys + "/",
        headers={
            'Accept': '*/*',
            'Accept-Language': 'zh-CN',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/81.0.4044.92 Safari/537.36'
        },
    )
    re.encoding = 'utf-8'
    soup = BeautifulSoup(re.text, 'html.parser')
    li = soup.find(class_="general clearfix").find_all(attrs={'doctype': "1"})
    flag = 1
    global sncom
    for list in li:
        img = list.find(class_="product-box").select("div div a img")[0].get("src")
        url = list.find(class_="product-box").find(name='div', class_="title-selling-point").select("a")[0].get("href")
        # 去查询历史价格
        try:
            historypriceinfo(url)
        except Exception as e:
            continue
        titles = list.find(class_="product-box").find(name='div', class_="title-selling-point").select("a")[0].text
        title = titles.replace('\n', '').replace(' ', '').replace('\r', '')
        try:
            deal = list.find(name='div', class_="info-evaluate").select("a i")[0].text
        except Exception as e:
            deal = None
        shop = list.find(name='div', class_="store-stock").select("a")[0].text
        location = "苏宁搜索"
        temp = (img, url, title, current, maxprice, maxdate, minprice, mindate, deal, shop, location)
        sncom.append(temp)
        flag = flag + 1
        if flag > 3:
            break
    # print(sncom)


commondity = []
price = []
pricecompare = []


#  这是保存搜索商品信息到数据库的处理
def saveinfo():
    try:
        sqlhelper.multiple_modify("replace into adminpg_commodity_info values(%s,%s,%s,%s,%s,%s)", commondity)
        sqlhelper.multiple_modify("insert into adminpg_price_info(dates,price,com_fk_id) values(%s,%s,%s)", price)
        sqlhelper.multiple_modify(
            "insert into adminpg_pricecompare(max_price,max_date,min_price,min_date,price_com_id_id) values(%s,%s,%s,%s,%s)",
            pricecompare)
        sqlhelper.close()
        return True
    except Exception as e:
        print(e)
        return False


def dosearch(request):
    ret = {'status': True, 'message': "", 'comdata': ""}
    if request.method == "GET":
        print("这是商品搜索的处理")
        searchtext = request.GET.get('comname')
        # 开始的时候需要清空里面的内容
        global searchcom
        searchcom = None
        print("搜索的内容：", searchtext)

        # 之前的接口
        # spider_jd_search(searchtext)
        # 现在直接去三个网站获取数据  然后去查历史价格
        jdinfo(searchtext)
        tianmao(searchtext)
        suning(searchtext)
        searchcom = tianmaos + jdcom + sncom
        ret['comdata'] = searchcom
        ret['status'] = True
        print("搜素成功！！")
        # if (saveinfo()):
        #     print("保存商品信息成功")
        # else:
        #     print("保存商品信息失败")
        print(searchcom)
        return HttpResponse(json.dumps(ret))


#  购物车的查询
jdcars = []
tbcars = []
sncars = []


# 获取京东的大图
def jdimgparse(url):
    old = url.split("jfs", 1)[1]
    head = "https://img12.360buyimg.com/cms/jfs"
    newimgurl = head + old
    return newimgurl


def spider_jd_cars():
    browser = Chrome()
    print("这是京东的购物车")
    browser.get("https://passport.jd.com/new/login.aspx?")
    while browser.current_url.startswith("https://passport.jd.com/new/login.aspx?"):
        print("等着京东的登录")
        time.sleep(1)
    browser.get("https://cart.jd.com/cart?")
    time.sleep(1)
    items = browser.find_element_by_class_name('item-list').find_elements_by_class_name("item-give")
    global jdcars
    for i in items:
        href = i.find_element_by_class_name("item-form").find_element_by_class_name(
            "goods-item").find_element_by_tag_name("a").get_attribute("href")
        # 根据href去查询最高最低的价格
        # try:
        #     jdsku = i.find_element_by_class_name("  item-item ").get_attribute("skuid")
        #     sku = str(jdsku) + "-3"
        #     maxminprice_list(sku)
        # except Exception as e:
        #     print("历史价格出错跳过")
        # jdsku = i.find_element_by_class_name("  item-item ").get_attribute("skuid")
        # sku = str(jdsku) + "-3"
        # maxminprice_list(sku)
        # print(jdsku)
        historypriceinfo(href)

        title = i.find_element_by_class_name("item-form").find_element_by_class_name("p-name").find_element_by_tag_name(
            "a").text

        img = i.find_element_by_class_name("item-form").find_element_by_class_name(
            "goods-item").find_element_by_tag_name("img").get_attribute("src")

        newimg = jdimgparse(img)

        pricenow = i.find_element_by_class_name("plus-switch").find_element_by_tag_name("strong").text
        price = pricenow.split("¥", 1)[1]

        temp = (newimg, href, title, price, maxprice, maxdate, minprice, mindate, None, "京东购物车", "京东官网")
        jdcars.append(temp)
    print(jdcars)
    browser.close()


def spider_taobao():
    browser = Chrome()
    browser.get("https://login.taobao.com/")
    while browser.current_url.startswith("https://login.taobao.com/"):
        print("等着淘宝的登录")
        time.sleep(2)
    browser.get("https://cart.taobao.com/")  # 淘宝购物车的网址
    time.sleep(5)
    items = browser.find_element_by_id("J_OrderList").find_elements_by_class_name("J_Order")
    global tbcars, hight_img, url, title, tb_price
    for i in items:
        try:
            title = i.find_element_by_class_name("item-basic-info").find_element_by_tag_name("a").get_attribute("title")
        except Exception as e:
            print(e)

        try:
            url = i.find_element_by_class_name("item-basic-info").find_element_by_tag_name("a").get_attribute("href")
            # 处理ulr得到uid
            # taobaosdk = url.split("=")[1]
            # print("淘宝sdk",taobaosdk)
            # requid = str(taobaosdk) + "-83"
            # maxminprice_list(requid)
            historypriceinfo(url)
        except Exception as e:
            print(e)

        from traceback import format_exc
        import re
        try:

            imgurl = i.find_element_by_class_name("item-pic").find_element_by_tag_name("img").get_attribute("src")

            # hight_img = "https://img.alicdn.com/bao/uploaded/i4" + imgurl.split("/i", 1)[1].split("jpg_", 1)[
            #     0] + "jpg_430x430.jpg"

            hight_img = re.sub("\d{2,3}[Xx]\d{2,3}", "430x430", imgurl)
        except Exception as e:
            print(format_exc())

        try:
            tb_price = \
                i.find_element_by_class_name("item-price").find_element_by_class_name("J_Price").text.split("￥", 1)[
                    1]
        except Exception as e:
            print(format_exc())

        temps = (hight_img, url, title, tb_price, maxprice, maxdate, minprice, mindate, None, "淘宝购物车", "淘宝")
        tbcars.append(temps)
    print(tbcars)
    browser.close()


def spider_suning():
    browser = Chrome()
    browser.get("https://passport.suning.com/ids/login?")
    while browser.current_url.startswith("https://passport.suning.com/ids/login?"):
        print("等着苏宁的登录")
        time.sleep(1)
    browser.get("https://shopping.suning.com/cart.do")
    time.sleep(1)
    items = browser.find_element_by_class_name("m-cart-body").find_elements_by_class_name("item-main")
    global sncars
    for i in items:
        try:
            imgurl = i.find_element_by_class_name("item-pic").find_element_by_tag_name("img").get_attribute("src")
            hight_img = imgurl.split("jpg_", 1)[0] + "jpg_800w_800h_4e"
        except Exception as e:
            continue

        try:
            title = i.find_element_by_class_name("item-info").find_element_by_tag_name("a").text
        except Exception as e:
            continue

        try:
            href = i.find_element_by_class_name("item-info").find_element_by_tag_name("a").get_attribute("href")
            # uid = snparse(href)
            # maxminprice_list(uid)
            historypriceinfo(href)
        except Exception as e:
            continue

        try:
            price = i.find_element_by_class_name("price-line").text.split("¥", 1)[1]
        except Exception as e:
            continue

        temp = (hight_img, href, title, price, maxprice, maxdate, minprice, mindate, None, "苏宁购物车", "苏宁网")
        sncars.append(temp)
    print(sncars)
    browser.close()


def searchcars(request):
    ret = {'status': True, 'message': "", 'cardatas': ""}
    if request.method == "GET":
        print("这是购物车查询的按钮！")
        jdstatus = request.GET.get('jd')
        tbstatus = request.GET.get('tb')
        snstatus = request.GET.get('sn')
        print("购物车数据状态：", jdstatus, tbstatus, snstatus, )
        cardata = []
        global jdcars
        global tbcars
        global sncars
        try:
            if jdstatus == "true":
                spider_jd_cars()
            if tbstatus == "true":
                spider_taobao()
            if snstatus == "true":
                spider_suning()
            cardata = jdcars + tbcars + sncars
            ret["cardatas"] = cardata
            ret["status"] = True
        except Exception as e:
            print(e)
            ret['status'] = False
        return HttpResponse(json.dumps(ret))
