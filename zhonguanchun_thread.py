# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 15:33:21 2019

@author:源大彪
@Comment:多线程
"""
import threading

class My_Thread(threading.Thread):
    def __init__(self,func,args=()):
        super(My_Thread,self).__init__()
        self.func = func
        self.args = args
        
    def run(self):
#        运行该线程后的操作
        self.resualt = self.func(*self.args)
    
    def get_resualt(self):
#        获取该线程运行后的返回值
        try:        
            return self.resualt
        except:
            
            return None