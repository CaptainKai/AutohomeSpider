import os
import re
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
import time
from multiprocessing import Pool


timeout = 5
socket.setdefaulttimeout(timeout)

class Crawler:

    def __init__(self, t = 0.1, word = "Baidu", spider_page_num=1, start_page=1):
        self._time_sleep = t
        self._amount = 0
        self._start_amount = 0
        self._header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        self._keyword = word
        self._save_path = os.path.join("./", word)
        self._start_amount = (start_page - 1) * 60
        self._amount = spider_page_num * 60 + self._start_amount
        self._counter = 0

    def save_image(self, image_info):
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        self._counter  = len(os.listdir(self._save_path)) + 1
        #print(image_info)
        try:
            time.sleep(self._time_sleep)
            image_url = image_info['objURL']
            fix = self.get_suffix(image_url)
            image_name = str(image_url).split("/")[-1].split('.')[0] + str(fix)
            urllib.request.urlretrieve(
                image_url,
                os.path.join(self._save_path, image_name)
            )
        except urllib.error.HTTPError as urllib_err:
            print(urllib_err)
        except Exception as err:
            time.sleep(1)
            print("Unknown Error: ", err)
        else:
            print("Picture: ", image_name, " get!")

    @staticmethod
    def get_suffix(name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return ".jpeg"

    def process_data(self, rsp_data):
        threadPool = Pool()
        for image_info in rsp_data['imgs']:
            threadPool.apply_async(self.save_image, args=(image_info,))
        threadPool.close()
        threadPool.join()

    @staticmethod
    def get_prefix(name):
        return name[:name.find('.')]

    def get_images(self):
        search = urllib.parse.quote(self._keyword)

        picture_nums = self._start_amount

        while picture_nums < self._amount:
            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' \
                  + search + '&cg=girl&pn=' + str(picture_nums) \
                  + '&rn=60&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'
            try:
                time.sleep(self._time_sleep)
                Req = urllib.request.Request(url=url, headers=self._header)
                page = urllib.request.urlopen(Req)
                rsp = page.read().decode('unicode_escape')
            except UnicodeDecodeError as err:
                print(err)
                print("------UnicodeDecodeErrorurl: ", url)
            except urllib.error.URLError as err:
                print("------UrlError: ", url, err)
            except socket.timeout as err:
                print("------socket timeout: ", url, err)
            else:
                rsp_data = json.loads(rsp)
                #print(rsp_data)
                self.process_data(rsp_data)

                #print("Load next page...")
                picture_nums += 60
                page.close()

        print("The download task is over. \nHave fun!")
        return

    def start(self):
        self.get_images()


if __name__ == "__main__":
    mycrawler = Crawler(0.2, "车牌照", 1000, 1)
    mycrawler.start()


