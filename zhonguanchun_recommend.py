# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 11:30:06 2019

@author: 源大彪
@Comment:推荐系统
"""
import zhonguanchun_dataRead
import zhonguanchun_thread
import re
import zhonguanchun_user
import csv
class CB_recomend():
#   基于内容推荐（ 城区距离的最近邻）
    def __init__(self):
        self.base_data = zhonguanchun_dataRead.read_phoneData()  
        self.maxmin_src = []
        self.maxmin_price = []
        self.maxmin_top = []
        self.recommend ={}
        self.phone = {}
        self.input_data = ''
        self.dis = {}
        self.input_ = {}
    def __max_min(self,data):
#        找出最大和最小值
        return [max(data),min(data)]
    def __find_top(self):
#        找出热榜排名的最大和最小值
        top = [int(self.base_data[i][j]['热榜排名']) for i in self.base_data for j in self.base_data[i]]
        self.maxmin_top = self.__max_min(top)
        return top
    def __find_maxmin_price(self):
        #        找出参考价格的最大和最小值
        top = [self.base_data[i][j]['参考价格'] for i in self.base_data for j in self.base_data[i] if self.base_data[i][j]['参考价格']]
        price = []
        for i in range(len(top)):
            if top[i][-1]=='万':
                price.append(float(top[i][:-1])*10000)
            elif top[i].isdigit():
                    price.append(int(top[i]))
            else:
                price.append(-1)
        self.maxmin_price =  self.__max_min(price)
        return price
    def __find_src(self):
#        找出得分的最大和最小值
        src = [float(self.base_data[i][j]['得分']) if self.base_data[i][j]['得分']!='' else -1 for i in self.base_data for j in self.base_data[i] ]
        self.maxmin_src =  self.__max_min(src)
        return src
    def __maidian(self):
#        找出所有的手机卖点
        phone_maidian = {}
        for i in self.base_data:
            for j in self.base_data[i]:               
                phone_maidian[j] = re.split('[， ]',self.base_data[i][j]['卖点'])
        return phone_maidian
    
    def __Rescaling(self):
#        归一化数据（除了价格参数，因为极值与均值差了太多）
        top = self.__find_top()
        price = self.__find_maxmin_price()
        src = self.__find_src()
        maidian = self.__maidian()
        inx = 0
        for i in self.base_data:
            for j in self.base_data[i]:
                t = (top[inx]-self.maxmin_top[1])/(self.maxmin_top[0]-self.maxmin_top[1])
                p = (price[inx]-self.maxmin_price[1])*300/(self.maxmin_price[0]-self.maxmin_price[1])
                s = (src[inx]-self.maxmin_src[1])/(self.maxmin_src[0]-self.maxmin_src[1])
                self.phone[j] = [t,p,s,maidian[j]]
                inx += 1
    
    def __deal_input(self,input_):
#        读取某款手机的具体数据
        self.input_[input_] = self.phone[input_]
    
    def __maidian_scr(self,data_part):
#        计算卖点相似性
        scr = 1
        for i in self.input_[self.input_data][3]:
            if i in data_part:
                scr -= 1/len(self.input_[self.input_data][3])
        return scr 
    
    def __distance(self,input_):
#        计算目标手机与某款手机的距离
        self.input_data = input_
        self.__deal_input(input_)
        dis_ = {}
        for i in self.phone:
            if i != input_:
                dis = sum([abs(self.phone[i][j]-self.input_[input_][j]) for j in range(3)])
                dis_[i] = dis+self.__maidian_scr(self.phone[i][3])
        return dis_
    def __commend(self,input_):
#        基于距离的远近整理出推荐顺序表
        dis_ = self.__distance(input_)
        dis = sorted(list(dis_.items()),key=lambda x:x[1])
        dis = {dis[i][0]:dis[i][1] for i in range(len(dis))}
        
        return [dis,input_]
    def all_comend(self):
#        计算所有手机彼此间的相对距离
        self.__Rescaling()
        thread_pool = []
        dis = {}
        for i in self.phone:
            thread_pool.append(zhonguanchun_thread.My_Thread(self.__commend,(i,)))
        for i in range(len(thread_pool)):
            thread_pool[i].start()
        for i in range(len(thread_pool)):
            thread_pool[i].join()
        for i in range(len(thread_pool)):
             an = thread_pool[i].get_resualt()
             dis[an[1]] = an[0]
        self.dis = dis
#        self.__save_all()
    def __save_all(self):
#        存储所有手机之间的相对距离
        str_temp = ['目标手机','其他手机','距离']
        csvfile = open('Phone/dis.csv', 'w', newline = '')
        writer_ = csv.writer(csvfile)
        writer_.writerow(str_temp)
        for i in self.dis:
            for j in self.dis[i]:
                try:
                    writer_.writerow([i,j,self.dis[i][j]])
                except:
                    print('无法写入'+i)
        csvfile.close()
    
    def commed_count(self,count): 
#        输出前count个所有手机的推荐列表
        self.all_comend()
        for i in self.dis:
            j = [list(self.dis[i].keys())[h] for h in range(count)]
            self.recommend[i] = {j[h]:self.dis[i][j[h]] for h in range(count)}
            
class CF_commend():
    def __init__(self,dis):
        self.user = ''   
        self.cb_dis = dis
        self.user_pool = zhonguanchun_user.generate_user(100)
        
    def __deal_sparsematrix(self,user_):
#        填充稀疏矩阵
        d_user = [i for i in user_]
        i_user = [i for i in self.user]
        s = list(set(i_user+d_user))
        user_i = {i:'' for i in s}
        user_d = {i:'' for i in s}
        for i in self.user:
            user_i[i] = self.user[i]
        for i in user_:
            user_d[i] = user_[i]
        for i in user_i:
            if user_i[i] == '':
                dis = self.cb_dis[i]
                dis = [dis[i] for i in i_user]
                user_i[i] = min(dis)
        for i in user_d:
            if user_d[i] == '':
                dis = self.cb_dis[i]
                dis = [dis[i] for i in d_user]
                user_d[i] = min(dis) 
        useri = [user_i[i] for i in user_i]
        userd = [user_d[i] for i in user_d]
        ans_ = {d_user[i]:user_[d_user[i]] for i in range(len(d_user)) if d_user[i] not in i_user}
        return ans_,self.__dis(useri,userd)        
    def recomand(self,input_user,count):
#        根据输入内容推荐count款产品
        self.__setUser(input_user)
        count += 1
        thread_pool = []
        neighbor = [100,100,100]
        neighbor_phone = [{},{},{}]
        for i in self.user_pool:
            thread_pool.append(zhonguanchun_thread.My_Thread(self.__deal_sparsematrix,(i,)))
        for i in range(len(thread_pool)):
            thread_pool[i].start()
        for i in range(len(thread_pool)):
            thread_pool[i].join()
        for i in range(len(thread_pool)):
             an = thread_pool[i].get_resualt()
#             print(str(an))
             max_n = max(neighbor)
             if an[1]<max_n:
                 inx = neighbor.index(max_n)
                 neighbor[inx] = an[1]
                 neighbor_phone[inx] = an[0]
        neib = list(zip(neighbor,neighbor_phone))
        if count>len(neib[0]):
            count = len(neib[0])
        s_ = list(neib[0][1].keys())
        
        s = list(s_)
        for j in range(len(neib)-1):  
            for i in s:
                if i not in neib[j+1][1]:
                    del s[s.index(i)]
            if s=={}:
                s = list(s_)
            else:
                s_ = list(s)
        return sorted([(i,neib[0][1][i]) for i in s_ ],key=lambda x:x[1], reverse=True)[:count]
        
        
    def __dis(self,user_i,user_d):
#        计算余弦相似度
        n = len(user_i)
        y = sum([user_i[i]*user_d[i] for i in range(n)])
        x = pow(sum([pow(user_i[i], 2) for i in range(n)]),0.5)+pow(sum([pow(user_d[i], 2) for i in range(n)]),0.5)
        return abs(y/x-1)
    def __setUser(self,input_user):
       self.user = input_user
def top3phone():
#    多线程的方式从各个表单中找出热榜排名前三的手机
    data = zhonguanchun_dataRead.read_phoneData()
    ans = {}
    thread_pool = []
    for i in data:
            thread_pool.append(zhonguanchun_thread.My_Thread(top3,(data[i],)))
    for i in range(len(thread_pool)):
        thread_pool[i].start()
    for i in range(len(thread_pool)):
        thread_pool[i].join()
    for i in range(len(thread_pool)):
         an = thread_pool[i].get_resualt()
         for i in an:
             ans[i] = an[i]
    return ans
def top3(data):
#    从某一表单中找出排名前三的数据
    rus = {}
    for i in data:
        if int(data[i]['热榜排名'])<=3 and data[i]['热榜排名']!='-1':
            rus[i] = data[i]
    return rus
if __name__=='__main__':
    b = CB_recomend()
    b.commed_count(5)
    r = b.recommend
    f = CF_commend(b.dis)
    ss = f.recomand({'HTC Desire 12s（全网通）': 0.3628769208906589,
 '三星GALAXY S8+（皇帝版/G9550/全网通）': 0.46567321405181217,
 '努比亚红魔Mars电竞手机（8GB RAM/全网通）': 0.055385546524169826,
 '华为nova 2青春版（全网通）': 0.47037934797176895,
 '国美K1（全网通）': 0.6971902053153645,
 '荣耀9（6GB RAM/全网通）': 0.22778221048362568,
 '诺基亚3310复刻版（移动/联通2G）': 0.2643410107685562,
 'Google Pixel 3 XL（双4G）': 0.5294629542445176,
 '魅族魅蓝Note 6（3GB RAM/全网通）': 0.10377222069429715},3)
 
    s = f.recomand({'HTC Desire 12s（全网通）': 0.3628769208906589,
 '三星GALAXY S8+（皇帝版/G9550/全网通）': 0.46567321405181217,
 '努比亚红魔Mars电竞手机（8GB RAM/全网通）': 0.055385546524169826,
 '华为nova 2青春版（全网通）': 0.47037934797176895,
 '国美K1（全网通）': 0.6971902053153645,
 '荣耀9（6GB RAM/全网通）': 0.22778221048362568,
 '诺基亚3310复刻版（移动/联通2G）': 0.2643410107685562,
 'Google Pixel 3 XL（双4G）': 0.5294629542445176,
 '魅族魅蓝Note 6（3GB RAM/全网通）': 0.9999},3)
    d = top3phone()