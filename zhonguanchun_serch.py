# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:34:54 2019

@author: 源大彪
@Comment:检索
"""


import zhonguanchun_dataRead
import re
import zhonguanchun_thread

class serch():
    def __init__(self, keyword,mode='0'):
        self.data =  zhonguanchun_dataRead.read_phoneData ()
        self.keyword = keyword
        self.keyword_list = []
        self.resualt = {}
        self.mode = mode#0:and 1:or
        
    def __keyword_spilt(self):
#        分割关键词
        self.keyword = re.sub('[\+\s]+',' ',self.keyword)
        inx = [i.start() for i in re.finditer('[\+\s]', self.keyword)]
        inx = [inx[i]-i for i in range(len(inx))]
        inx.insert(0,0)
        keyword = re.sub('[\+\s]','',self.keyword)
        inx.append(len(keyword))
        self.keyword_list = [keyword[inx[i]:inx[i+1]] for i in range(len(inx)-1)]
        print(self.keyword_list)
    
    def __serch_key(self,keyword,data,name):
#        搜索单一关键词
        data_ = name+''.join([data[i] for i in data])
        if re.search(keyword,data_,re.IGNORECASE)!=None:
#            print('搜索成功')
            return [data,name]

    
    def __serch_one(self,keyword):
#        用多线程的方式，将数据和某款手机信息进行比对（主要调用__serch_key）
        treading_pool = []
        resulat = {}
        for i in self.data:
            data = self.data[i]
            for j in data:
                treading_pool.append(zhonguanchun_thread.My_Thread(self.__serch_key,(keyword,data[j],j)))
        for i in range(len(treading_pool)):
            treading_pool[i].start()
        for i in range(len(treading_pool)):
            treading_pool[i].join()
        for i in range(len(treading_pool)):
            data = treading_pool[i].get_resualt()
            try:
                resulat[data[1]] = data[0]
            except:
                continue
        if resulat=={}:
            print('数据库没有收录该数据')
            return None
#        print(str(resulat))
        return resulat
    
    def __serch_allkey(self):
#        将分割后的关键词用多线程的方式搜索（调用__serch_one）
        treading_pool = []
        ans = []
        for i in self.keyword_list:
            treading_pool.append(zhonguanchun_thread.My_Thread(self.__serch_one,(i,)))
        for i in range(len(treading_pool)):   
            treading_pool[i].start()
        for i in range(len(treading_pool)):
            treading_pool[i].join()
        for i in range(len(treading_pool)):
            ans.append(treading_pool[i].get_resualt())
        return ans
    
    def serch__all(self):
#        一个汇总函数
        self.__keyword_spilt()
        ans = self.__serch_allkey()
        if self.mode=='0':
            de = self.__intersection_data(ans)
            if de!= None:
                self.resualt = {i:ans[de[1]][i] for i in de[0]}
        else:
            self.resualt  = {j:ans[i][j] for i in range(len(ans)) for j in ans[i]}
            
            
    def __intersection_data(self,data):
#        取各关键词之间的交集
        for i in data:
            if i == None:
                return 
        ans = []
        size = [len(i) for i in data]
        size_min = min(size)
        inx_min = size.index(size_min)
        data_  = list(data[inx_min])
        for i in data_:
            for j in range(len(data)):
                name = [h for h in data[j]]
                if i not in name:
#                    print('没得')
                    break
            else:
                ans.append(i)
        return [ans,inx_min]
if __name__  ==  '__main__':
    s = serch('小米 骁龙 概念产品','0')
    s.serch__all()
    data = s.resualt

    
   