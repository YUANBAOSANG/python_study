# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 21:34:44 2019

@author: 源大彪
"""
import random
import zhonguanchun_dataRead
class user():
    def __init__(self):
        self.user ={}  
    def set_user(self,name,score):
#        设置self.user
        self.user[name] = score
def generate_user(count):
#    产生随机用户数据
    data = zhonguanchun_dataRead.read_phoneData()
    Artificial_user = []
    for j in range(count//3):
        Artificial_user.append({j:random.random() for i in data for j in data[i]  if random.random()<0.01 })
    for j in range(count//3):
        Artificial_user.append({j:random.random() for i in data for j in data[i]  if random.random()<0.1 })
    for j in range(count//3):
        Artificial_user.append({j:random.random() for i in data for j in data[i]  if random.random()<0.3 })
    return Artificial_user   
