# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 20:54:26 2019

@author: 源大彪

"""
import tkinter
import zhonguanchun_serch
import zhonguanchun_recommend
import re
import zhonguanchun_user
class GUI():
    def __init__(self):
        # 创建主窗口,用于容纳其它组件
        self.flag = 0
        self.user = zhonguanchun_user.user()
        self.root = tkinter.Tk()
        # 给主窗口设置标题内容
        self.root.title("手机查询")
        # 创建一个输入框,并设置尺寸
        self.ip_input = tkinter.Entry(self.root,width=40)
        # 创建一个回显列表
        self.display_info = tkinter.Listbox(self.root,height=25,width=400)
        self.display_info.insert(0,'欢迎使用简单粗暴的手机安利系统~')
        # 创建一个查询结果的按钮
        self.serch_button = tkinter.Button(self.root, command = self.__ok, text = "确定")
        self.serch_data = {}
        self.CBrecomand = zhonguanchun_recommend.CB_recomend()
        self.CBrecomand.commed_count(100)
        self.recomCB = self.CBrecomand.recommend
        self.CFrecomand = zhonguanchun_recommend.CF_commend(self.CBrecomand.dis)
    def __ok(self):
#        根据输入内容和提示内容进入对应的搜索部分
        keyword = self.ip_input.get()
        if keyword=='快放假了':
                self.flag += 1
        if len(self.serch_data)==1 and re.search('0\.[0123456789]+分',keyword) != None:
            name = list(self.serch_data.keys())[0]
            self.user.set_user(name,float(keyword[:-1]))
            if self.display_info.get(0) == '你之前的评分为:':
                self.display_info.delete(1)
                self.display_info.insert(1,'  '+str(self.user.user[name]))
            else:        
                self.display_info.delete(0)
            self.__recom(name)
        
            
        else:
            
            if self.flag>=5 and keyword=='快放假了':
                self.display_info.delete(0,10)
                self.display_info.insert(0,'暑假快到了，预祝大家玩得愉快，噢不对，学得愉快，考研加油！')
            else:
                self.__serch(keyword)
    def __recom(self,name):
        inx = self.inx
        print(self.display_info.get( inx))
        if self.display_info.get( inx) != '推荐一波~~~~~~':
            self.display_info.insert( inx,'推荐一波~~~~~~')
        inx+=1
        print(str(self.user.user))
        CB_rcname = self.__CBrecomand(name)
        if len(self.user.user)>=5:
            CF_rcname = self.__CFrecommand()[0][0]   
            if CB_rcname!= self.display_info.get(inx):
                self.display_info.insert( inx,CB_rcname)
            inx+=1
            print(CF_rcname)
            if CF_rcname!= self.display_info.get(inx):
                self.display_info.delete(inx)
                self.display_info.insert( inx,CF_rcname)
        else:
            print(self.display_info.get( inx))
            if CB_rcname!= self.display_info.get(inx):
                self.display_info.insert(inx,CB_rcname)
    def __serch(self,keyword):
#        搜索
        self.display_info.delete(0,20000000)
        s = zhonguanchun_serch.serch(keyword,'0')
        s.serch__all()
        self.serch_data = s.resualt
        if len(self.serch_data)==0:
            if self.user.user == {}:
                self.display_info.insert(0,'找不到找不到,要不看看热榜top3都有啥吧~')
                top3 = zhonguanchun_recommend.top3phone()
                name = list(top3.keys())
                self.display_info.insert(1,'为你检索到以下'+str(len(name))+'款:')
                for i in name:
                    self.display_info.insert(2,'  '+i)
            else:
                self.display_info.insert(0,'找不到找不到,你可能会喜欢它们~')
                max_user = self.__findUserMax()
                cb = self.__CBrecomand(max_user)
                self.display_info.insert(1,cb)
                if len(self.user.user)>=5:
                    CF_rcname = self.__CFrecommand()[0][0]
                    self.display_info.insert(3,CF_rcname)
        else:        
            
            if len(self.serch_data)==1:
                name = list(self.serch_data.keys())[0]
                self.inx =  self.__display(0,self.serch_data)
                if self.__exist_user(name):
                    self.display_info.insert(0,'你可以更改你的评分，格式0.x分')
                    self.display_info.insert(0,'  '+str(self.user.user[name]))
                    self.display_info.insert(0,'你之前的评分为:')
                    self.inx += 3
                    self.__recom(name)
                    
                else:
                    self.display_info.insert(0,'请你给该手机打分,格式为0.x分')
            else:
                name = list(self.serch_data.keys())
                self.display_info.insert(0,'为你检索到以下'+str(len(name))+'款:')
                for i in name:
                    self.display_info.insert(1,'  '+i)
            
    def __display(self,count,data):
#        显示单一手机的结构化数据
        for i in data:
            self.display_info.insert(count,i)
            count+=1
            for j in data[i]:
                if j =='配置':
                    self.display_info.insert(count,'    '+j+':')
                    count+=1
                    d = re.findall("'.*?\],",data[i][j])
                    if d==[]:
                        self.display_info.insert(count,'        无配置信息')
                        count+=1
                    else:
                        for k in d:
                            self.display_info.insert(count,'        '+k)
                            count+=1
                elif j=='卖点':
                    self.display_info.insert(count,'    '+j+':')
                    count+=1
                    d = re.split('[\s，]',data[i][j])
                    for k in d:
                            self.display_info.insert(count,'        '+k)
                            count+=1
                else:
                    self.display_info.insert(count,'    '+j+':'+data[i][j])
                    count+=1
        return count
    def __CFrecommand(self):
#        调用CF推荐算法
        return self.CFrecomand.recomand(self.user.user,1)
    def __CBrecomand(self,name):
#        调用CB推荐算法的内容，并查重
        CB_rcname = list(self.recomCB[name].keys())
        for i in CB_rcname:
            if i not in self.user.user:
                return i
        else:
            return '--------'
    def __findUserMax(self):
#        查找用户评分最高的产品
        v = list(self.user.user.values())
        max_vinx = v.index(max(v))
        return list(self.user.user.keys())[max_vinx]
    def __exist_user(self,name):
#        判断该款产品是否存在与用户评分字典中
        v = list(self.user.user.keys())
        return name in v
    def gui_arrang(self):
#        GUI的装配
        self.root.geometry('500x500')
        self.ip_input.pack()
        self.display_info.pack()
        self.serch_button.pack()
        self.root.resizable(0,0)
        
if  __name__=='__main__':
    g = GUI()
    g.gui_arrang()
    g.root.resizable(0,0)
    tkinter.mainloop()