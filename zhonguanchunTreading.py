# -*- coding: utf-8 -*-
"""
Created on Sat Jul 6 20:56:25 2019

@author: 源大彪
@Comment:多线程爬取中关村手机品牌top50以及对应品牌下手机，本机4~7分钟
"""

from bs4 import BeautifulSoup
import requests
import re
import random
import urllib.request
import os
import threading
import time
import csv

class zhonguanchun():
    def __init__(self):
        self.header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3226.400 QQBrowser/9.6.11681.400',
                    }
        self.timeout = random.choice(range(80, 180))
        self.head = 'http://detail.zol.com.cn'
        self.phone_ = {}#品牌名：[{手机型号：[链接具体内容的url,图片url,卖点，参考价格,得分,热榜排名,id(int),{配置（7个参数）或者没爬出来一个参数}]},总数]
        self.best_ = ['高通骁龙855','6400万','4000万','12G','10000mAh','1440*2560']
        self.phone_id_ = 0
        self.shared_resource_lock = threading.RLock()
        self.treading_pool_ = []
        self.treading_pool_1 = []
        self.brand_ = {}#品牌对应网址，品牌图标，获取评分，价格区间，目前产品总数（#已删去以具体子页面为准）,占有率，关注度，好评率
    def testTreadingread_brandTop50Url(self):
#        对测试该类
        self.__read_brandTop50Url()
    
    def __read_brandTop50Url(self):
        #本函数实现爬取受关注的Top50品牌的信息
        #品牌对应网址，品牌图标，获取评分，价格区间，目前产品总数（#已删去以具体子页面为准）,占有率，关注度，好评率
        tread_pool = []
        url = 'http://top.zol.com.cn/compositor/57/manu_attention.html'
        req = requests.get(url,headers=self.header, timeout=self.timeout)
        reqt = re.search('<div class="rank-list__cell cell-2">(?:\n.+)+</div>',req.text).group(0)
        soup = BeautifulSoup(reqt, 'html.parser')
        for i in soup.find_all('div',class_="rank-list__cell cell-2"):
            #爬取品牌名和对应品牌子连接和品牌图标连接
            f = i.find('div',class_="brand_logo")
            a = f.find('a',class_='pic')
            brand_url = a['href']
            img_url = a.find('img')['src']
            a = f.find('p').find('a')
            name_ = a.string
            url_set = [brand_url,img_url]
            self.brand_[name_] = url_set
            
    
            t1 = threading.Thread(target=self.read_allPhone,args=(brand_url,name_))
            tread_pool.append(t1)
            t2 = threading.Thread(target=self.read_photoB,args=(img_url,name_))
            t2.start()

            t2.join()
            
            
        keys = list(self.brand_.keys())
        count = 0
        for i in soup.find_all('div',class_="rank-list__cell cell-3"):
            #爬取评分
            f = i.find('div',class_="score clearfix")
            s = f.find('span')
            url1 = self.brand_[keys[count]][0]
            url2 = self.brand_[keys[count]][1]
            self.brand_[keys[count]] = [url1,url2,s.string]
            count+=1
        count = 0
        for i in soup.find_all('div',class_="rank-list__cell cell-7"):
            #爬取手机价格区间和总数
            f = i.find('div',class_="rank__price")
            p = re.search('<div class="rank__price">&amp;yen(.+)<a',str(f)).group(1)
#            s = f.find('a').find('span').string
            url1 = self.brand_[keys[count]][0]
            url2 = self.brand_[keys[count]][1]
            ping = self.brand_[keys[count]][2]
            self.brand_[keys[count]] = [url1,url2,ping,p]
            count+=1
        count = 0
        for i in soup.find_all('div',class_="rank-list__cell cell-4"):
            #爬取市场占有率
            url1,url2,ping,jia = self.brand_[keys[count]]
            z = re.search('\n\t\t\t\t\t\t\t(.+)\t\t\t\t\t\t',str(i.string)).group(1)
            if z=='-':
                z = '0%'
            self.brand_[keys[count]] = [url1,url2,ping,jia,z]
            count+=1
        count = 0
        for i in soup.find_all('div',class_="rank-list__cell cell-5"):
            #爬取关注度
            s = i.find('div',class_="rate-bar").find('span')['style']
            url1,url2,ping,jia,z = self.brand_[keys[count]]
            self.brand_[keys[count]] = [url1,url2,ping,jia,z,re.search('width: (.+)',str(s)).group(1)]
            count+=1
        count = 0
        for i in soup.find_all('div',class_="rank-list__cell cell-6"):
            #爬取好评率
            url1,url2,ping,jia,z,g = self.brand_[keys[count]]
            self.brand_[keys[count]] = [url1,url2,ping,jia,z,g,i.string]
            count+=1 
        
        for i in range(len(tread_pool)):
            tread_pool[i].start()
        for i in range(len(tread_pool)):
            tread_pool[i].join()
#        print(self.brand_)
        
        
    def __read_phone(self,url,name):
        #本函数实现爬取任意一个品牌的手机大致参数，返回一个字典 品牌名：{手机型号：链接具体内容的url,卖点，参考价格，得分,}
        #每一页有48个手机，用总数除以48算出页数。
        #构造网页就是将最后的list_1变成list_n
        req = requests.get(url,headers=self.header, timeout=self.timeout)
#        print(url)
        count = re.search('<span class="total">共 <b>(.*)</b> 款</span>',req.text).group(1)
        page = (int(count)+47)//48
        phone_ ={}
        cou = 1
        treading_pool = []
        treading_pool_1 = []
        for p in range(1,page+1):
            url = list(url)
            url[-6] = str(p)
            url = ''.join(url)
            req = requests.get(url,headers=self.header, timeout=self.timeout)
            tex = re.search('<ul id="J_PicMode" class="clearfix">(?:\n.*)*</ul>\n.*<div class="adSpace"',req.text).group(0)
            soup = BeautifulSoup(tex, 'html.parser')
#            print(str(p))
            
            for t in soup.find_all('li'): 
#                if(cou>int(count)):
#                    break
#                cou+=1
                #获取型号和特色,以及具体网址,图片url
                #获取图片url
#                print(t)
                a = t.find('a')
                if(a==None):
                    img_url = 'None'
                else:  
#                print(a)
                    a=a.find('img')
                    if(a==None):
                        img_url = 'None'
                    else:
                        img_url = a['.src']
                
                a = t.find('h3')
                if(a==None):
                    continue
                a = a.find('a')
                url_phone = self.head+a['href']
                phone_name =re.sub('） +(?:.+)','）',a.text)
                t2 = threading.Thread(target=self.read_photoAP,args=(img_url,str(self.phone_id_),name))
                treading_pool_1.append(t2)
                t2 = threading.Thread(target=self.read_allPhoneParameter,args=(url_phone,name,phone_name))
                treading_pool.append(t2)
                phone_feature = a.find('span').string
                #获取参考价格
                phone_paice = t.find('div',class_="price-row").find('b',class_="price-type").string
                #获取评分
                phone_rale = t.find('div',class_="comment-row").find('span',class_='score')
                if(phone_rale==None):
                    phone_rale = -1
                else:
                    phone_rale = phone_rale.string
                #获取热榜排名
                phone_top = t.find('div', class_="rank-row")
                if(phone_top==None):
                    phone_top = -1
                else:
                    phone_top = phone_top.find('a')
                    phone_top = phone_top.find('span').string
#                print(str(cou)+' '+str([img_url,url_phone,phone_feature,phone_paice,phone_rale,phone_top]))
                
                phone_[phone_name] = [img_url,url_phone,phone_feature,phone_paice,phone_rale,phone_top,self.phone_id_]#网址，特色，参考价格，评分(-1为无评分)，热榜排名(-1为未上榜)
#                print('  '+str(cou))
                cou+=1
                self.shared_resource_lock.acquire()
                self.phone_id_+=1
                self.shared_resource_lock.release()
#        print('phone'+count)
        self.treading_pool_1.append(treading_pool_1)
        self.treading_pool_.append(treading_pool)
#        for i in range(len(treading_pool)):
#            treading_pool[i].start()
#            time.sleep(1)
#        for i in range(len(treading_pool)):
#            treading_pool[i].join()
#        treading_pool[0].start()
#        treading_pool[0].join()
        
        return phone_,count
     
    def read_allPhone(self,url,name):
        print('read_allPhon:'+name)
        phone_set,count  = self.__read_phone(url,name)
        
        self.phone_[name] = [phone_set,count]
          
          
    def __read_phoneParameter(self,url):
#        爬取手机的配置
        #返回配置名：[配置，优先于多少手机，行业内目前最好的]
        req = requests.get(url,headers=self.header, timeout=self.timeout)
        
        if(re.search('<a  href="(.+)"  target="_self">参数',req.text)==None):
            print('爬不出来，淦，网页结构不同0')
            return {"网页结构":"不一样0"}
        url_parameter = self.head+re.search('<a  href="(.+)"  target="_self">参数',req.text).group(1)
#        print(url_parameter)
        req = requests.get(url_parameter,headers=self.header, timeout=self.timeout)
#        f = open('teatreq.txt','w',encoding='utf-8')
#        f.write(req.text)

#        tag = re.search('<div class="wrapper clearfix mt30">',req.text).group(0)
#        print(tag)
        soup = BeautifulSoup(req.text, 'html.parser')
        if(soup.find('div',class_="wrapper clearfix mt30")==None):
            print('爬不出来，淦，网页结构不同1')
            return {"网页结构":"不一样1"}
        t = soup.find('div',class_="wrapper clearfix mt30").find('div',class_="info-list-fr").find('ul').find_all('li')
        
        
            
        parameter_ = {}
        for li in t:
            one_ = li.find('div',class_="box-item-fl")
            #获取参数名称
            name_ = one_.find('label').string
            #获取参数值
            value_ = one_.find('a')
            if (value_==None):
                value_ = one_.find('span',class_="product-link")
            value_ = value_.string
            value_ = re.sub('\s','',value_)
            #获取优先率和行业最好
            tow_=li.find('div',class_="box-item-fr")
            
#            #获取行业最好
#            if(len(self.best_)<7):
#                best_ = tow_.find('span',class_="text-r").find('font').string
#                self.best_.append(best_)
            #获取优先率 
            
            if(tow_!=None):
                priority_=tow_.find('div',class_="box-bar").find('i').string
            else:
                priority_ = '无排名'
            
            parameter_[name_] = [value_,priority_]
#            print(parameter_)
        return parameter_
    
    
    def read_allPhoneParameter(self,url,bread_name,phone_name):
#        获取所有信息
        print('read_allPhoneParameter:'+bread_name+' '+phone_name)
        parameter_ = self.__read_phoneParameter(url)
#        self.shared_resource_lock.acquire()
        self.phone_[bread_name][0][phone_name].append(parameter_)
#        self.shared_resource_lock.release()
        
    def read_photoB(self,url,name):
#        获取品牌图片
        name_ = name
        path = 'Phone/brand'
        
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        urllib.request.urlretrieve(url,path+'/{name}.png'.format(name=name_))
            
    def read_photoAP(self,url,name,bread_name):
#        获取手机图片
        bread_name = re.sub('\s','',bread_name)
        path_ = 'Phone/phone/'+bread_name
#        name_ = re.sub('[/:\n\\*?"]','_',name) 
        urllib.request.urlretrieve(url,path_+'/{name}.jpg'.format(name=name))
    
    
    def deal_treaingpool(self,pool):
#        运行和守护线程池里的线程
        for i in pool:
            for j in range(len(i)):
                i[j].start()
        for i in self.treading_pool_:
            for j in range(len(i)):
                i[j].join()
        
    def __write_data_phone(self,name):
#        写入某品牌的手机具体数据
        str_temp = ['型号','卖点','参考价格','得分','热榜排名','id','配置']
        path_ = 'Phone/phone/'
        csvfile = open(path_+name+'.csv', 'w', newline = '')
        writer_ = csv.writer(csvfile)
        writer_.writerows(('品牌：',[name]))
        part_ = self.phone_[name][0]
        writer_.writerow(str_temp)
        for j in part_:
#            print(part_[j])
            if len(part_[j])==8:
                writer_.writerow([j,part_[j][2],part_[j][3],part_[j][4],part_[j][5],str(part_[j][6]),part_[j][7]])
            else:
                writer_.writerow([j,part_[j][2],part_[j][3],part_[j][4],part_[j][5],str(part_[j][6]),'无返回配置参数'])
        csvfile.close()
    
    def data_phone_thread(self):
#        用多线程的方式按品牌写入具体手机的数据
        thread_pool = []
        for name in self.phone_:
           t1 = threading.Thread(target=self.__write_data_phone,args=(name,))
           thread_pool.append(t1)
        for i in range(len(thread_pool)):
            thread_pool[i].start()
        for i in range(len(thread_pool)):
            thread_pool[i].join()
        
    def write_data_bread(self):
#        写品牌数据
        str_temp = ['品牌名','获取评分','价格区间','目前产品总数','占有率','关注度','好评率']
        csvfile = open('Phone/bread.csv', 'w', newline = '')
        writer_ = csv.writer(csvfile)
        writer_.writerow(str_temp)
        for i in self.brand_:
            print(self.brand_[i])
            try:
                writer_.writerow([i,self.brand_[i][2],self.brand_[i][3],self.phone_[i][1],self.brand_[i][4],self.brand_[i][5],self.brand_[i][6]])
            except:
                print('无法写入'+i)
                writer_.writerow([i])
        csvfile.close()
        
    def build_path(self):
#        新建read_photoAP以及write_data_phone所用文件夹。
        for i in self.brand_:
            path_ = 'Phone/phone/'+i
            if not os.path.exists(path_):
                os.makedirs(path_)
                    
                
                
    
if __name__=='__main__':
    start = time.time()
    t = zhonguanchun()
    t.testTreadingread_brandTop50Url()
    t.build_path()
    t.deal_treaingpool(t.treading_pool_)
    t.deal_treaingpool(t.treading_pool_1)
    t.data_phone_thread()
    t.write_data_bread()
#    s = t.phone_
#    b = t.brand_
    end = time.time()
    print(str(end-start))