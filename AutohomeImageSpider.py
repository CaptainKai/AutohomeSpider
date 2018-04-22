# coding: utf-8
import os
import requests
from lxml import etree
import time
import sys

IMAGESET_PATH = "../Images/"
ROOT_URL = "https://car.autohome.com.cn"
ALL_BRANDS_URL = "/AsLeftMenu/As_LeftListNew.ashx?typeId=2%20&brandId=0%20&fctId=0%20&seriesId=0"


def download(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    try:
        html = requests.get(url, headers=headers)
        res = html.text.encode(html.encoding, "ignore").decode(html.encoding, "ignore")
        return res
    except Exception as e:
        print("Can't download %s." % (url))
        return None


# 获取汽车品牌列表
def get_brand_list(url):
    html = download(url)
    brand_list = []
    if html is not None:
        page_tree = etree.HTML(html)
        hrefs = page_tree.xpath("//a")
        for href in hrefs:
            brand = dict()
            brand_name = href.xpath("./text()")
            if brand_name and href.get('href', None):
                brand['href'] = href.get('href', None)
                brand['name'] = brand_name[0]
            brand_list.append(brand)
    return brand_list


# 获取每个汽车品牌的汽车型号列表
def get_cartype_list(url):
    html = download(url)
    cartype_list = []
    if html is not None:
        page_tree = etree.HTML(html)
        type_area = []
        for i in range(15):
            type_area.extend(page_tree.xpath("/html/body/div[2]/div[1]/div[2]/div[%d]/div/div[2]/div/ul/*" %(i)))
        for type_ in type_area:
            type_href = type_.xpath("./div/span/a")
            type_name = type_.xpath("./div/span/a/text()")
            if type_href and type_name:
                type_href = type_href[0]
                type_name = type_name[0]
                one_type = dict()
                one_type['href'] = type_href.get('href', None)
                one_type['name'] = type_name
                cartype_list.append(one_type)
    return cartype_list


# 获得每个汽车型号的图片地址列表
def get_pic_list(url):
    html = download(url)
    pics_list = []
    if html is not None:
        page_tree = etree.HTML(html)
        appearance_pics = None
        for i in range(2, 5):
            appearance_pics = page_tree.xpath("/html/body/div[2]/div[1]/div[2]/div[7]/div/div[%d]/div[1]/a[2]" %(i))
            if appearance_pics:
                break
        if appearance_pics:
            pics_url = appearance_pics[0].get('href', None)
            while pics_url != None:
                pics_html = download(ROOT_URL + pics_url)
                if pics_html is not None:
                    pics_tree = etree.HTML(pics_html)
                    pics_area = pics_tree.xpath("/html/body/div[2]/div[1]/div[2]/div[7]/div/div[2]/div[2]/ul/*")
                    for pic_ in pics_area:
                        pic_href = pic_.xpath("./a/img")[0]
                        one_img = dict()
                        one_img['href'] = pic_href.get('src', None)
                        one_img['name'] = pic_href.get('title', None)
                        pics_list.append(one_img)
                    more_pages = pics_tree.xpath("/html/body/div[2]/div[1]/div[2]/div[7]/div/div[3]/div/*")
                    if len(more_pages) > 0:
                        next_page = more_pages[-1]
                        pics_url = next_page.get('href', None)
                        if pics_url == "javascript:void(0);":
                            pics_url = None
                    else:
                        pics_url = None
    return pics_list



def mainWork(root_url=ROOT_URL+ALL_BRANDS_URL, interval=0.85, start_brand="ABT"):
    brand_list = get_brand_list(root_url)
    flag = False
    for brand in brand_list:
        brand_name = brand.get('name', None)
        brand_href = brand.get('href', None)
        if brand_name == start_brand:
            flag = True

        if flag and brand_name is not None and brand_href is not None:
            if brand_name.find(":") != -1:
                brand_name = brand_name.replace(":", "-")
            cartype_list = get_cartype_list(ROOT_URL + brand_href)
            for cartype in cartype_list:
                cartype_href = cartype.get('href', None)
                cartype_name = cartype.get('name', None)
                if cartype_name.find(":") != -1:
                    cartype_name = cartype_name.replace(":", "-")
                if cartype_name is not None and cartype_href is not None:
                    cartype_path = brand_name + '_' + cartype_name
                    pic_list = get_pic_list(ROOT_URL + cartype_href)
                    for pic in pic_list:
                        pic_href = pic.get('href', None)
                        pic_name = pic.get('name', None)
                        if pic_href is not None and pic_name is not None:
                            image_name = pic_href.split('/')[-1]
                            if image_name.find(":") != -1:
                                image_name = image_name.replace(":", "-")
                            if pic_name.find(":") != -1:
                                pic_name = pic_name.replace(":", "-")
                            image_path = os.path.join(IMAGESET_PATH, cartype_path)
                            if not os.path.exists(image_path):
                                os.makedirs(image_path)
                            image_save_name = os.path.join(image_path, image_name)
                            if not os.path.exists(image_save_name):
                                try:
                                    image = requests.get("https:" + pic_href)
                                    with open(image_save_name, 'wb') as f:
                                        f.write(image.content)
                                        f.close()
                                        print("Download %s successfully." % (image_save_name))
                                        time.sleep(interval)
                                except Exception as e:
                                    print("Download %s failed." % (image_save_name))
                                    continue
        else:
            continue


if __name__ == "__main__":
    mainWork(root_url=ROOT_URL + ALL_BRANDS_URL, interval=0.2, start_brand="奥迪")