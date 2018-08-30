# -*- coding: utf-8 -*-
import scrapy
import re
import time
import hashlib
import json
from video_scrapy.items import *
def r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)
def match1(text, *patterns):
    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret
class VideoSpider(scrapy.Spider):
    name = 'video'
    handle_httpstatus_list = [404]
    get_playlist=True
    start_num=None
    end_num=None
    m3u8_error={}
    def __init__(self, my_url=None, my_playlist=False,start_num=None,end_num=None,*args, **kwargs):
        super(VideoSpider, self).__init__(*args, **kwargs)
        if my_url is None:
            self.start_urls = []
        else:
            self.start_urls = ["%s"%my_url]
        if isinstance(my_playlist, str):
            if my_playlist=="True":
                my_playlist=True
            elif my_playlist=="False":
                my_playlist=False
            else:
                print("my_playlist:%s"%my_playlist)
        else:
            print(type(my_playlist))
            print(my_playlist)
        self.get_playlist=my_playlist
        if start_num is not None:
            self.start_num=int(start_num)
        if end_num is not None:
            self.end_num=int(end_num)
    def start_requests(self):
        print("start_requests")
        bili_url=[]
        iqiyi_url=[]
        for url in self.start_urls:
            if "bilibili" in url:
                bili_url.append(url)
                self.start_urls.remove(url)
            elif "iqiyi.com" in url:
                iqiyi_url.append(url)
                self.start_urls.remove(url)
        for i in bili_url:
            yield scrapy.Request(url=i, callback=self.bili_parse)
        for i in iqiyi_url:
            if self.get_playlist:
                yield scrapy.Request(url=i, callback=self.iqiyi_parse,meta={"all":None,"dont_redirect":True,"handle_httpstatus_list":[302]})
            else:
                yield scrapy.Request(url=i, callback=self.iqiyi_parse,meta={"dont_redirect":True,"handle_httpstatus_list":[302]})
        for i in self.start_urls:
            pass
    def iqiyi_parse(self,response):
        print("iqiyi_parse")
        if isinstance(response.body, bytes):
            html=response.body.decode()
        else:
            html=str(response.body)
        if "iqiyi.com/v" in response.url:
            if "all" in response.meta:
                temp=re.search(r'"?albumId"?:\s*(\d+)',html)
                if temp:
                    albumid=int(temp.group(1))
                    url="http://cache.video.iqiyi.com/jp/avlist/%d/1/"%(albumid)
                    yield scrapy.Request(url=url,callback=self.iqiyi_get_list)
                else:
                    with open("error.txt", "a") as f:
                        f.write('\n')
                        f.write(str(nowTime))
                        f.write('\n')
                        f.write("can't find albumid for %s"%(response.url))
                    
            else:
                tvid = r1(r'#curid=(.+)_', response.url) or \
                       r1(r'tvid=([^&]+)', response.url) or \
                       r1(r'data-player-tvid="([^"]+)"', html) or r1(r'tv(?:i|I)d=(.+?)\&', html) or r1(r'param\[\'tvid\'\]\s*=\s*"(.+?)"', html)
                videoid = r1(r'#curid=.+_(.*)$', response.url) or \
                          r1(r'vid=([^&]+)', response.url) or \
                          r1(r'data-player-videoid="([^"]+)"', html) or r1(r'vid=(.+?)\&', html) or r1(r'param\[\'vid\'\]\s*=\s*"(.+?)"', html)
                if tvid is None:
                    yield scrapy.Request(url=response.url,callback=self.iqiyi_parse,meta=response.meta,dont_filter=True)
                else:
                    info_u = 'http://mixer.video.iqiyi.com/jp/mixin/videos/' + tvid
                    yield scrapy.Request(url=info_u,callback=self.iqiyi_get_info,meta={"tvid":tvid,"videoid":videoid,"url":response.url},dont_filter=True)
        else:
            if self.get_playlist:
                temp=re.search(r'"?albumId"?:\s*(\d+)',html)
                if temp:
                    albumid=int(temp.group(1))
                    url="http://cache.video.iqiyi.com/jp/avlist/%d/1/"%(albumid)
                    yield scrapy.Request(url=url,callback=self.iqiyi_get_list)
                else:
                    with open("error.txt", "a") as f:
                        f.write('\n')
                        f.write(str(nowTime))
                        f.write('\n')
                        f.write("can't find albumid for %s"%(response.url))
            else:
                with open("error.txt", "a") as f:
                    f.write('\n')
                    f.write(str(nowTime))
                    f.write('\n')
                    f.write("can't find video for %s"%(response.url))

        # if "iqiyi.com/v" not in response.url:
        #     if self.get_playlist:
        #         temp=re.search(r'"?albumId"?:\s*(\d+)',html)
        #         if temp:
        #             albumid=int(temp.group(1))
        #             # yield scrapy.Request(url=link,callback=self.iqiyi_parse,dont_filter=True)
        #         # my_list=response.xpath('//p[@class="site-piclist_info_title"]/a[text()]')
        #         # if self.start_num is not None and self.end_num is not None:
                    # for index,value in enumerate(my_list, start=1):
                    #     if int(index)>=int(self.start_num) and int(index)<=int(self.end_num):
                    #         link=value.xpath("./@href").extract()[0]
                    #         if "www." in link:
                    #             if link[0]=="w":
                    #                 link="http://"+link
                    #             elif link[0]=="/":
                    #                 link="http:"+link
                    #         elif link[0]=="/":
                    #             link=response.url+link
                    #         print("send %s"%link)
                    #         yield scrapy.Request(url=link,callback=self.iqiyi_parse,dont_filter=True)
        #         else:
        #             for index,value in enumerate(my_list, start=1):
        #                 link=value.xpath("./@href").extract()[0]
        #                 if "www." in link:
        #                     if link[0]=="w":
        #                         link="http://"+link
        #                     elif link[0]=="/":
        #                         link="http:"+link
        #                 elif link[0]=="/":
        #                     link=response.url+link
        #                 print("send %s"%link)
        #                 yield scrapy.Request(url=link,callback=self.iqiyi_parse,dont_filter=True)
        # else:
        #     if "all" in response.meta:
        #         link=response.xpath("//h1/a/@href").extract()[0]
        #         if "www." in link:
        #             if link[0]=="w":
        #                 link="http://"+link
        #             elif link[0]=="/":
        #                 link="http:"+link
        #         elif link[0]=="/":
        #             link=response.url+link
        #         yield scrapy.Request(url=link,callback=self.iqiyi_parse)
        #     else:
        #         tvid = r1(r'#curid=(.+)_', response.url) or \
        #                r1(r'tvid=([^&]+)', response.url) or \
        #                r1(r'data-player-tvid="([^"]+)"', html) or r1(r'tv(?:i|I)d=(.+?)\&', html) or r1(r'param\[\'tvid\'\]\s*=\s*"(.+?)"', html)
        #         videoid = r1(r'#curid=.+_(.*)$', response.url) or \
        #                   r1(r'vid=([^&]+)', response.url) or \
        #                   r1(r'data-player-videoid="([^"]+)"', html) or r1(r'vid=(.+?)\&', html) or r1(r'param\[\'vid\'\]\s*=\s*"(.+?)"', html)
        #         info_u = 'http://mixer.video.iqiyi.com/jp/mixin/videos/' + tvid
        #         yield scrapy.Request(url=info_u,callback=self.iqiyi_get_info,meta={"tvid":tvid,"videoid":videoid,"url":response.url},dont_filter=True)
    def iqiyi_get_list(self,response):
        print("iqiyi_get_list")
        if isinstance(response.body, bytes):
            html=response.body.decode()
        else:
            html=str(response.body)
        temp_dict = json.loads(html[len('var tvInfoJs='):])
        if temp_dict["code"]== 'A00000':
            mylist=temp_dict["data"]["vlist"]
            if self.start_num is not None and self.end_num is not None:
                for index,value in enumerate(mylist, start=1):
                    if int(index)>=int(self.start_num) and int(index)<=int(self.end_num):
                        link=value["vurl"]
                        if "www." in link:
                            if link[0]=="w":
                                link="http://"+link
                            elif link[0]=="/":
                                link="http:"+link
                        elif link[0]=="/":
                            link=response.url+link
                        print("send %s"%link)
                        yield scrapy.Request(url=link,callback=self.iqiyi_parse,priority=100-index,dont_filter=True,meta={"dont_redirect":True,"handle_httpstatus_list":[302]})
            else:
                for index,value in enumerate(mylist, start=1):
                    link=value["vurl"]
                    if "www." in link:
                        if link[0]=="w":
                            link="http://"+link
                        elif link[0]=="/":
                            link="http:"+link
                    elif link[0]=="/":
                        link=response.url+link
                    print("send %s"%link)
                    yield scrapy.Request(url=link,callback=self.iqiyi_parse,priority=100-index,dont_filter=True,meta={"dont_redirect":True,"handle_httpstatus_list":[302]})

    def iqiyi_get_info(self,response):
        print("iqiyi_get_info")
        try:
            self.state
            try:
                if "m3u8_error" in self.state:
                    self.m3u8_error = self.state["m3u8_error"]
                else:
                    self.state["m3u8_error"]=self.m3u8_error
            except:
                pass
        except:
            pass
        if isinstance(response.body, bytes):
            html=response.body.decode()
        else:
            html=str(response.body)
        temp_dict = json.loads(html[len('var tvInfoJs='):])
        name = temp_dict["name"]
        tvid=response.meta["tvid"]
        videoid=response.meta["videoid"]
        t = int(time.time() * 1000)
        src = '76f90cbd92f94a2e925d83e8ccd22cb7'
        key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
        sc = hashlib.new('md5', bytes(str(t) + key  + videoid, 'utf-8')).hexdigest()
        url = 'http://cache.m.iqiyi.com/tmts/{0}/{1}/?t={2}&sc={3}&src={4}'.format(tvid,videoid,t,sc,src)
        self.m3u8_error.setdefault(name, {}).setdefault("url", response.meta["url"])
        yield scrapy.Request(url=url,callback=self.iqiyi_get_json,meta={"name":name})
    def iqiyi_get_json(self,response):
        print("iqiyi_get_json")
        if isinstance(response.body, bytes):
            temp_dict = json.loads(response.body.decode())
        else:
            temp_dict = json.loads(str(response.body))
        if temp_dict["code"]== 'A00000':
            high_id = {10: '4k', 19: '4k', 5:'BD', 18: 'BD', 4: 'TD', 17: 'TD_H265',  14: 'TD'}
            low_id={96: 'LD',2: 'HD',1: 'SD',21: 'HD_H265'}
            print(temp_dict)
            temp_list=temp_dict["data"]["vidl"]
            is_high=False
            for item in temp_list:
                if int(item["vd"]) in high_id:
                    url=item["m3u"]
                    is_high=True
                    yield scrapy.Request(url=url,callback=self.m3u8_parse,meta={"name":response.meta["name"]})
                    break
            if not is_high:
                for item in temp_list:
                    if int(item["vd"]) in low_id:
                        url=item["m3u"]
                        yield scrapy.Request(url=url,callback=self.m3u8_parse,meta={"name":response.meta["name"]})
                        break
        else:
            import datetime
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open("error.txt", "a") as f:
                f.write('\n')
                f.write(str(nowTime))
                f.write('\n')
                f.write("can't play %s"%str(response.meta["name"]))

    def m3u8_parse(self, response):
        print("m3u8_parse")
        try:
            self.state
            try:
                if "m3u8_error" in self.state:
                    self.m3u8_error = self.state["m3u8_error"]
                else:
                    self.state["m3u8_error"]=self.m3u8_error
            except:
                pass
        except:
            pass
        url = response.url
        name = response.meta['name']
        self.m3u8_error.setdefault(name,{})
        if isinstance(response.body, bytes):
            page = response.body.decode('ascii')
        else:
            page = str(response.body)
        file_line = page.split("\n")
        if int(response.status) !=200:
            yield scrapy.Request(url=response.url,callback=self.m3u8_parse,dont_filter=True)
        else:
            if file_line[0] != "#EXTM3U":
                if len(response.body)==0:
                    yield scrapy.Request(url=self.m3u8_error[name]["url"],callback=self.iqiyi_parse,dont_filter=True,meta={"dont_redirect":True,"handle_httpstatus_list":[302]})
                else:
                    with open("m3u8_page.txt", "a") as f:
                        f.write(response.url)
                        f.write("\n")
                        f.write(str(response.body))
                        f.write("\n")
                    raise BaseException("非M3U8的链接")
            else:
                unknow = True  # 用来判断是否找到了下载的地址
                i = 1
                for index, line in enumerate(file_line):
                    if "EXTINF" in line:
                        unknow = False
                        if file_line[index + 1][0:4] == "http":
                            pd_url = file_line[index + 1]
                        else:
                            if file_line[index + 1][0] != '/':
                                pd_url = url.rsplit(
                                    "/", 1)[0] + "/" + file_line[index + 1]
                            else:
                                pd_url = url.rsplit(
                                    "/", 1)[0] + file_line[index + 1]
                        if self.m3u8_error.setdefault(name, {}).setdefault("error_num", 0) == 0:
                            yield scrapy.Request(pd_url, callback=self.savefile,
                                                     meta={'fileid': int(i), 'name': name, 'end': False, "id": None, "filetype": "ts","m3u8":None})
                        else:
                            if int(i) in self.m3u8_error.setdefault(name, {}).setdefault("error", []):
                                yield scrapy.Request(pd_url, callback=self.savefile,
                                                     meta={'fileid': int(i), 'name': name, 'end': False, "id": None, "filetype": "ts","m3u8":None})
                        i = i + 1
                    if "ENDLIST" in line:
                        if self.m3u8_error.setdefault(name, {}).setdefault("error_num", 0) != 0:
                            self.m3u8_error[name]["send_num"] = self.m3u8_error[name]["error_num"]
                        else:
                            self.m3u8_error[name]["send_num"] = i - 1
                        if self.check_m3u8_has_error(name):
                            if "bilibili" in self.m3u8_error[name]["url"]:
                                yield scrapy.Request(url=self.m3u8_error[name]["url"],callback=self.bili_parse,dont_filter=True)
                            elif "iqiyi.com" in self.m3u8_error[name]["url"]:
                                yield scrapy.Request(url=self.m3u8_error[name]["url"],callback=self.iqiyi_parse,dont_filter=True,meta={"dont_redirect":True,"handle_httpstatus_list":[302],"m3u8":None})
                            else:
                                pass
                        item = FileItem()
                        item["id"] = None
                        item['fileid'] = i
                        item['name'] = name
                        item['end'] = True
                        item['content'] = b''
                        item['filetype'] = 'ts'
                        yield item
                if unknow:
                    raise BaseException("未找到对应的下载链接")
                else:
                    print("下载请求完成 m3u8 %s" % name)
    def check_m3u8_has_error(self,name):
        print("check_m3u8_has_error")
        try:
            self.state
            try:
                if "m3u8_error" in self.state:
                    self.m3u8_error = self.state["m3u8_error"]
                else:
                    self.state["m3u8_error"]=self.m3u8_error
            except:
                pass
        except:
            pass
        print(self.m3u8_error)
        if name not in self.m3u8_error:
            return False
        else:
            self.m3u8_error[name].setdefault("get_num", 0)
            if "send_num" in self.m3u8_error[name]:
                if int(self.m3u8_error[name]["send_num"]) == int(self.m3u8_error[name]["get_num"]):
                    if len(self.m3u8_error[name].setdefault("error", [])) == 0:
                        self.m3u8_error.pop(name)
                    else:
                        self.m3u8_error[name]["get_num"] = 0
                        self.m3u8_error[name]["error_num"] = len(
                            self.m3u8_error[name]["error"])
                        self.m3u8_error[name].pop("send_num")
                        return True
            return False
    def parse(self, response):
        pass
    def bili_parse(self,response):
        print("bili_parse")
        if isinstance(response.body, bytes):
            file = str(response.body.decode("utf8"))
        else:
            file = str(response.body)
        temp = re.search(r"__INITIAL_STATE__=(\{.*\});\(fun", file, re.S)
        temp = str(temp.group(1))
        temp = json.loads(temp)
        url = "https://www.kanbilibili.com/api/video/%d/download?cid=%d&quality=64&page=%d"
        if "videoData" in temp:
            videodata = temp['videoData']
            pagelist = videodata['pages']
            aid = videodata["aid"]
            for item in pagelist:
                page = item['page']
                cid = item['cid']
                name = item['part']
                new_url = url % (int(aid), int(cid), int(page))
                yield scrapy.Request(url=new_url, callback=self.bili_get_json, meta={"name": name, "id": page, "Referer": response.url})
        else:
            title = temp["mediaInfo"]["title"]
            pagelist = temp["epList"]
            name = str(title) + "%03d"
            for item in pagelist:
                aid = item["aid"]
                cid = str(item["cid"])
                page = item["index"]
                access_id = int(item["episode_status"])
                if access_id == 2:
                    if len(item["index_title"]) == 0:
                        new_name = name % (int(page))
                    else:
                        new_name = title + "_" + item["index_title"]
                    if "bangumi" in response.url:
                        secretkey = "9b288147e5474dd2aa67085f716c560d"
                        temp = "cid=%s&module=bangumi&otype=json&player=1&qn=112&quality=4" % (
                            str(cid))
                        sign_this = hashlib.md5(
                            bytes(temp + secretkey, 'utf-8')).hexdigest()
                        new_url = "https://bangumi.bilibili.com/player/web_api/playurl?" + \
                            temp + '&sign=' + sign_this
                    else:
                        new_url = url % (int(aid), int(cid), int(page))
                    yield scrapy.Request(url=new_url, callback=self.bili_get_json, meta={"name": new_name, "id": page, "Referer": response.url})
                else:
                    pass
    def bili_get_json(self, response):
        print("bili_get_json")
        if isinstance(response.body, bytes):
            temp_dict = json.loads(response.body.decode())
        else:
            temp_dict = json.loads(str(response.body))
        if "err" in temp_dict:
            if temp_dict['err'] is None:
                my_url_list = temp_dict["data"]["durl"]
                filetype = temp_dict["data"]["format"][0:3]
                end_id = len(my_url_list)
                for i in my_url_list:
                    fileid = i["order"]
                    link_url = i["url"]
                    if int(fileid) == int(end_id):
                        end = True
                    else:
                        end = False
                    yield scrapy.Request(url=link_url, callback=self.savefile, headers={"Origin": "https://www.bilibili.com", "Referer": response.meta["Referer"]},
                                         meta={"name": response.meta["name"], "id": response.meta["id"], "filetype": filetype, "fileid": fileid, "end": end,"download_timeout":4800})
        else:
            my_url_list = temp_dict["durl"]
            filetype = temp_dict["format"][0:3]
            end_id = len(my_url_list)
            for i in my_url_list:
                fileid = i["order"]
                link_url = i["url"]
                if int(fileid) == int(end_id):
                    end = True
                else:
                    end = False
                yield scrapy.Request(url=link_url, callback=self.savefile, headers={"Origin": "https://www.bilibili.com", "Referer": response.meta["Referer"]},
                                     meta={"name": response.meta["name"], "id": response.meta["id"], "filetype": filetype, "fileid": fileid, "end": end,"download_timeout":4800})
    def savefile(self, response):
        print("savefile")
        try:
            self.state
            try:
                if "m3u8_error" in self.state:
                    self.m3u8_error = self.state["m3u8_error"]
                else:
                    self.state["m3u8_error"]=self.m3u8_error
            except:
                pass
        except:
            pass
        item = FileItem()
        if response.meta['fileid'] is None and response.meta['end'] is None:
            print("get %s" % (response.meta['name']))
            item['fileid'] = None
            item['end'] = None

        else:
            print("get %s__%d" %
                  (response.meta['name'], int(response.meta['fileid'])))
            item['fileid'] = int(response.meta['fileid'])
            item['end'] = response.meta['end']
            if response.meta['id'] is None:
                item['id'] = None
            else:
                item['id'] = int(response.meta['id'])
        name=item['name'] = str(response.meta['name']).encode(
        ).translate(None, b'\\/:*?"<>|').decode()
        item['filetype'] = response.meta['filetype']
        if "m3u8" in response.meta:
            self.m3u8_error[response.meta["name"]]["get_num"] = self.m3u8_error[
                response.meta["name"]].setdefault("get_num", 0) + 1
            if int(response.status) == 404:
                if int(response.meta['fileid']) in self.m3u8_error[response.meta["name"]].setdefault("error", []):
                    pass
                else:
                    self.m3u8_error[response.meta["name"]].setdefault(
                        "error", []).append(int(response.meta["fileid"]))
            else:
                if int(response.meta["fileid"]) in self.m3u8_error[response.meta["name"]].setdefault("error", []):
                    self.m3u8_error[response.meta["name"]][
                        "error"].remove(int(response.meta["fileid"]))
                item['content'] = response.body
                yield item
            if self.check_m3u8_has_error(name):
                if "bilibili" in self.m3u8_error[name]["url"]:
                    yield scrapy.Request(url=self.m3u8_error[name]["url"],callback=self.bili_parse,dont_filter=True)
                elif "iqiyi.com" in self.m3u8_error[name]["url"]:
                    yield scrapy.Request(url=self.m3u8_error[name]["url"],callback=self.iqiyi_parse,dont_filter=True,meta={"dont_redirect":True,"handle_httpstatus_list":[302]})
                else:
                    pass
        else:
            item['content'] = response.body
            yield item