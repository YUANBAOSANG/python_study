 ＃SDUST EE专业小学期项目：爬取新闻、电影、音乐、电商数据，并做分析与统计和推荐
 
 ##爬虫：爬取了中关村的Top50品牌的手机（共1682款）价格、得分、热榜排名、配置等信息。
 
 ##检索：多关键词 and 或者 or 逻辑检索。
 
 ##推荐：使用了基于内容推荐算法和基于用户评分的协同过滤算法（稀疏矩阵的处理方式参考了 [1]基于项目评分预测的协同过滤推荐算法.邓爱林,  朱扬勇,  施伯乐[D].上海:复旦大学 计算机与信息技术系,2003.）
）。
 
 
＃使用说明：

#zhonguanchunTreading.py爬虫，优先运行获取数据。

zhonguanchun_user.py用户类，设置用户信息以及生成用户集信息（用于基于用户评分的协同过滤算法，谁叫我菜爬不到用户评分呢，只能自己造了。）

zhonguanchun_thread.py线程类

zhonguanchun_serch.py检索类，实现对手机的任意部分进行or 或者 and 逻辑检索

zhonguanchun_recommend.py推荐类，CB基于内容推荐，CF基于用户评分推荐。

zhonguanchun_dataRead.py 数据读取类

zhonguanchun_datapic.py数据可视化，如果需要对一些品牌数据的统计，可以运行该文件或者按照需要修改。

#zhonguanchun_GUI.py GUI界面，读取完数据后可以之间运行该文件即可。

 
