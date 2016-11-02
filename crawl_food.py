#!/usr/bin/env python 
#coding:utf-8

import  requests,re,pickle
from bs4 import BeautifulSoup


class gather_food(object):
    def __init__(self,url= "http://home.meishichina.com/recipe/{}/page/{}/",foodtype={}):
        self.url = url
        self.food = foodtype
        self.fooddict = {}
        self.foodurl = []
    def food_name(self):
        for foodtype in self.food:
            for i in range(50):
                self.foodurl.append(self.url.format(foodtype,i))
        value = []
        for url in self.foodurl:
            print url
            try:
                content = requests.get(url).content
            except Exception,e:
                    print e
            soup = BeautifulSoup(content,'lxml')
            ul = soup.find_all('div',class_="detail")

            for li in ul:
                #print  li.find('h2').a.string
                a = unicode(li.find('h2').a.string).encode('utf8')
                value.append(a)
        self.fooddict['美食']= value
        return self.fooddict
if __name__ =="__main__":
    url = "http://home.meishichina.com/recipe/{}/page/{}/"

    foodtype = {'zhongshicaixi': '中式菜'#, 'chuancai': "川菜", 'lucai': "鲁菜", 'yuecai': "粤菜", 'mincai': "闽菜", 'sucai': "苏菜",
                #'zhecai': "浙菜", 'xiangcai': "湘菜", 'huicai': "徽菜", 'huaiyangcai': " 淮扬菜", 'yucai': "粤菜", 'jinci': "晋菜",
                #'ecai': "鄂菜", 'yunnancai': "云南菜", 'beijingcai': "北京菜", 'dongbeicai': "东北菜", 'xibeicai': "西北菜",
                #'guizhoucai': "贵州菜", 'shanghaicai': "上海菜", 'xinjiangcai': "新疆菜", 'kejiacai': "客家菜",
                #'taiwanmeishi': "台湾美食", 'xianggangmeishi': "香港美食", 'aomenmeishi': "澳门美食", 'gancai': "赣菜"
                }

    a = gather_food(url,foodtype).food_name()
    with open('food.txt','w') as fp:
        pickle.dump(a,fp)
    print len(a['美食'])