# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 15:36:09 2019

@author: 源大彪
"""

import zhonguanchun_thread
import os
import csv

def read_phonepath():
#    读取目标目录下所有csv的名称
    file_list = os.listdir('Phone/phone/')
    return [i for i in file_list if i[-1]=='v']

def read_data(path):
#    读取某目录下的csv数据
    csvfile = open(path, 'r')
    read = csv.reader(csvfile)
    list_ = [i for i in read]
#    print(str(list_[0]))
    if list_[0][0]=='品':
        list_ = list_[2:]
#    print(str(list_))
    bread = {}
    title = list_[0]
    for i in list_[1:]:
        bread[i[0]] = {title[h]:i[h] for h in range(1,len(i))}
    return bread

def read_phoneData():
#    读取所有的手机数据
    filename = read_phonepath()
    treading_pool = []
    phone_data = {}
    path_ = 'Phone/phone/'
    for i in filename:
        treading_pool.append(zhonguanchun_thread.My_Thread(read_data,(path_+i,)))
    for i in range(len(treading_pool)):
        treading_pool[i].start()
    for i in range(len(treading_pool)):
        treading_pool[i].join()
    for i in range(len(treading_pool)):
       phone_data[filename[i]]  = treading_pool[i].get_resualt()
    return phone_data

def read_dis():
#    读取CB算法所算出的距离数据
#    不建议使用此函数，用起来比直接运算还慢(滑稽)
    csvfile = open('Phone/dis.csv', 'r')
    read = csv.reader(csvfile)
    
    list_ = [i for i in read]
    list_ = list_[1:]
    bread = {}
    for i in list_:
        bread[i[0]] = {i[1]:i[2] for h in range(1647)}
    return bread