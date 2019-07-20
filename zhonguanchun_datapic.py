# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 15:16:54 2019

@author: 源大彪
@Comment:数据处理与可视化
"""
import os
import uuid
import matplotlib.pyplot as plt
import re
import zhonguanchun_dataRead
import jieba
from wordcloud import WordCloud

plt.rcParams['font.sans-serif'] = ['SimHei']


def histogram(data,path,pic_name,xlable_,ylabel_,title_):
#    画直方图
    #data的结构为名称:数值的字典
    plt.figure(figsize=(10,5)) 
    key = [i for i in data]
    value = [data[i] for i in data]
    plt.bar(range(len(value)), value,color='rgb')
    plt.xticks(range(len(value)),key,size='small',rotation=30)
    plt.xlabel(xlable_)
    plt.ylabel(ylabel_)
    plt.title(title_)
    for a,b in zip(range(len(value)),value):
        plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=7)
    plt.savefig(path+'/'+pic_name+".jpg")
    plt.show()    

def boxplot(data,title,pic_name,path,xlabel,ylabel):
#    画箱型图
    plt.figure(figsize=(20,20))
    labels = [i[:-5] for i in data]
    all_data = [data[i] for i in data]
#    print(str(len(labels)))
#    print(str(len(all_data)))
    bplot = plt.boxplot(all_data, patch_artist=True, labels=labels)  # 设置箱型图可填充
    plt.title(title)
    
    colors = ['#'+str(uuid.uuid4()).replace('-','')[:6] for _ in range(len(all_data))]
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)  # 为不同的箱型图填充不同的颜色
    

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(path+'/'+pic_name+".jpg")
    plt.show()



def pie(data,path,pic_name):
#    画饼图
    #data的结构为名称:数值的字典
    key = [i for i in data]
    value = [data[i] for i in data]
    plt.figure(figsize=(10,10)) #调节图形大小
    patches,text1,text2 = plt.pie(value,
                          labels=key,
                          labeldistance = 1.2,#图例距圆心半径倍距离
                          autopct = '%3.2f%%', #数值保留固定小数位
                          shadow = False, #无阴影设置
                          startangle =90, #逆时针起始角度设置
                          pctdistance = 0.6) #数值距圆心半径倍数距离
    #patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部文本
    # x，y轴刻度设置一致，保证饼图为圆形
    plt.axis('equal')
    plt.legend()
    plt.savefig(path+'/'+pic_name+".jpg")
    plt.show()


def plot_bread_scoTOP10_histogram(data):
#    找出前10得分品牌的数据用以画直方图
    key = [i for i in data]
    selet_data = {key[i]:float(data[key[i]]['获取评分'][:-1]) for i in range(10)}
    histogram(selet_data,'Phone/deal_data',u'top10得分',u'品牌',u'得分',u'手机品牌top10')

def plot_bread_OccupancyTOP10_pie(data):
#    找出前十占有率的品牌数据用以画饼图
    key = [i for i in data]
    selet_data = {key[i]:float(data[key[i]]['占有率'][:-1]) for i in range(10)}
    pie(selet_data,'Phone/deal_data','top10占有率')  

def plot_bread_AttentionTOP10_pie(data):
#    找出前十受关注度的品牌数据用以画饼图
    key = [i for i in data]
    selet_data = {key[i]:float(data[key[i]]['关注度'][:-1]) for i in range(10)}
    pie(selet_data,'Phone/deal_data','top10关注度') 

def dict_str2float(data,label):
#    字典中的string转数字，用以转换好评率
    for i in data:
        data[i][label] = float(re.search('[1234567890]+',data[i][label]).group(0))
    return data


    
def plot_bread_praiseTop10_pie(data):
#    找出前十受好评率的品牌数据用以画饼图
    data = dict_str2float(data,'好评率')
    sort_data = sorted(data.items(),key=lambda x:x[1]['好评率'],reverse=True)
    #除去市场占有率为0的品牌
    sort_data = {sort_data[k][0]:sort_data[k][1] for k in range(len(sort_data)) if sort_data[k][1]['占有率']!='0%'}
    key = [i for i in sort_data]
    selet_data = {key[i]:data[key[i]]['好评率'] for i in range(10)}
    histogram(selet_data,'Phone/deal_data',u'top10好评率',u'品牌',u'好评率',u'手机品牌top10') 

    

    


def statistical_price_box(data):
#    找出各数据的价格用以画箱型图
    selet_data = {}
    for i in data:
        if i=='VERTU .csv':
            h = [float(data[i][j]['参考价格'][:-1])*10000 for j in data[i]]
            boxplot({i:h},u'VERTU手机箱型图','VERTU手机箱型图','Phone/deal_data','品牌','价格')
            continue
        pire_list = []
        for j in data[i]:
            
            try:
                num = int(data[i][j]['参考价格'])
            except:
                continue
            else:
                pire_list.append(num)
        selet_data[i] = pire_list
    
    boxplot(selet_data,u'TOP50价格箱型图','TOP50价格箱型图','Phone/deal_data','品牌','价格')

def peizhi_wordcloud(data):
#    检索有排名的手机的配置关键字用以做词云
    word = []
    plt.figure(figsize=(10,10))
    for i in data:
        for j in data[i]:
            if data[i][j]['热榜排名']=='-1' or data[i][j]['配置']=="{'网页结构': '不一样1'}":
                continue
            w = re.sub("[像素英寸'\[]",' ',''.join(re.findall("\['.+?'",data[i][j]['配置'])))
            word.append(w)
    wordcloud(word,"Phone/deal_data/配置词云.jpg")
   
def madian_wordcloud(data):
    #    检索有排名的手机的卖点关键字用以做词云
    word = []
    plt.figure(figsize=(10,10))
    for i in data:
        for j in data[i]:
            if data[i][j]['热榜排名']=='-1':
                continue
            if re.findall(":.+?\s",data[i][j]['卖点'])==[]:
                word.append(data[i][j]['卖点'])
                continue
            w = re.sub("[英寸像素联通电信移动]",'',''.join(re.findall(":.+?\s",data[i][j]['卖点'])))
            word.append(w)
    wordcloud(word,"Phone/deal_data/卖点词云.jpg")
         
def wordcloud(word,path):
#    word是一个个列表
#    作词云啊
    cut_text = " ".join(jieba.cut(''.join(word)))
    wordcloud = WordCloud(font_path="C:/Windows/Fonts/simfang.ttf",
                          background_color="white",width=1000,height=880).generate(cut_text)
    plt.imshow(wordcloud, interpolation="bilinear")
    
    plt.axis("off")
    plt.savefig(path)
    plt.show()

def build_path():
#    建立所需的文件夹格式
    path_ = 'Phone/deal_data'
    if not os.path.exists(path_):
        os.makedirs(path_)

if __name__=='__main__':
    build_path()
    bread_data = zhonguanchun_dataRead.read_data('Phone/bread.csv')
    phone_data = zhonguanchun_dataRead.read_phoneData()
    plot_bread_scoTOP10_histogram(bread_data)
    plot_bread_OccupancyTOP10_pie(bread_data)
    plot_bread_AttentionTOP10_pie(bread_data)
    plot_bread_praiseTop10_pie(bread_data)
    statistical_price_box(phone_data)
    peizhi_wordcloud(phone_data)
    madian_wordcloud(phone_data)

    
    
    
    
    
    