#!/usr/bin/env python 
#coding:utf-8

import Queue
import threadpool
import time
import urllib
from lxml import etree

import requests,pickle,json,os
from bs4 import BeautifulSoup

from conf.config import foodtype,names
from crawl_food import gather_food
from write_exal import writeexal


class fengjing(object):
    def __init__(self, demourl="https://zhidao.baidu.com/search?word={}++%3F&ie=gbk&site=-1&sites=0&date=0&pn={}",names={}):
        self.demourl = demourl
        self.names = names
        self.jdurl = []
        self.url = {}
        self.content = {}
        self.contentmax = {}
        self.noneurl = {}
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": 'keep-alive',
            }
    def has_key(self):
        klist = []
        for i in os.listdir('result'):
            if i.endswith('_lt240.xls'):
                m = i.split('_')[0][4:].decode('gbk').encode('utf8')
                klist.append(m)
        return klist
    def get_url(self):
        haskey = self.has_key()
        count = 0
        for local, jidian in self.names.items():
            for name in jidian:

                if name in haskey:
                    print 'has',name
                    continue

                name2 = urllib.urlencode({"word": '%s  ?' % name})
                for num in range(70):
                    self.jdurl.append(self.demourl.format(name2, num))
                self.question_and_url()
                self.question_and_answer()
                name1 = local + name
                try:
                    writeexal(self.content, name1.decode('utf8').encode('gbk'), 'lt240')
                    writeexal(self.contentmax, name1.decode('utf8').encode('gbk'), 'gt240')
                except:pass
                #调试信息输出代码
                #writeexal(self.noneurl, name1.decode('utf8').encode('gbk'))
                count = count + len(self.content.keys())
                print count,len(self.contentmax.keys())
                #设置断点抓取多少后停止
                if count >= 10000:
                    print 'the process is run down'
                    break
                self.jdurl = []
                self.url = {}
                self.content = {}
                self.contentmax = {}
                self.noneurl = {}

        #print 'frist jdurl', len(self.jdurl)

    def question_and_url(self):

        t = 1
        start = time.time()

        q = Queue.Queue()

        for u in self.jdurl:
            q.put(u)
        lst = [q.get() for i in range(q.qsize())]
        pool = threadpool.ThreadPool(10)
        requests = threadpool.makeRequests(self.thread_guangxi, lst)
        for req in requests:
            try:
                pool.putRequest(req)
            except Exception,e:
                print e

        pool.wait()
        end = time.time()
        #print "all url time %s" % (end - start)
        #print "all url number %s" % len(self.url.keys())

    def question_and_answer(self):
        start = time.time()
        q = Queue.Queue()

        for u in self.url:
            q.put(u)
        lst = [q.get() for i in range(q.qsize())]
        pool = threadpool.ThreadPool(10)
        #requests = threadpool.makeRequests(self.thread_answer, lst)
        requests = threadpool.makeRequests(self.thread_answer_etree, lst)
        t = 1
        n = 1
        for req in requests:
            try:
                pool.putRequest(req)
            except Exception,e:
                print e
            t += 1
            if t == 100:
                print 'clraw 100 of the number is %s' % n
                n += 1

                t = 1
        pool.wait()
        end = time.time()
        print "all answer time %s" % (end - start)
        #print "all answer number %s" % len(self.url.keys())

    def thread_guangxi(self, u):
        #目前在用的抓取规则、通用知道内容
        content = requests.get(u,timeout=5).content
        soup = BeautifulSoup(content, 'lxml')
        ##print  soup.prettify()
        dl = soup.find_all('dl', class_="dl")

        for i in dl:

            question = i.find('a', class_='ti').text
            if len(question) > 25:
                continue
            # print i.find('a',target='_blank')['href']
            URL = i.find('a', target='_blank')['href']
            self.url[URL] = question

    def thread_question(self, u):
        #废弃 抓取标签不够优化
        content = requests.get(u).content

        if content is None:
            return None
        soup = BeautifulSoup(content, 'lxml')
        dt = soup.find_all('dt', class_="dt mb-4 line")
        # print dt
        # print len(dt)
        for i in dt:
            question = i.a.text
            if len(question) > 25:
                continue
            URL = i.a['href']
            self.url[URL] = question


    def thread_answer_etree(self, u):
        content = requests.get(u, headers=self.headers, timeout=5).content
        if content is None: return None
        root = etree.HTML(content)
        question = root.xpath("//span[@class='ask-title ']/text()")[0]
        #import pdb;pdb.set_trace()
        answer = root.xpath("//pre[@accuse='aContent']/text()")
        print  question, len(answer)
        if len(answer) is None:
            return  None
        elif len(answer) > 240:
            self.contentmax[question] = answer
        elif len(answer) > 0:
            self.content[question] = answer
        time.sleep(0.5)

    def thread_answer(self, u):
        # 线程池执行抓取到百度知道最佳答案，筛选过滤到
        # for i in self.url:

        content = requests.get(u, timeout=5).content
        # print u,len(content)
        soup = BeautifulSoup(content, 'lxml')
        question = self.url[u]
        # question = soup.find('span', class_="ask-title").string
        pre = soup.find('pre', accuse="aContent")
        if pre == None:
            # self.noneurl[u] = question
            pass
        else:
            answer = ''.join(pre.text.split())
            if len(answer) > 240:
                self.contentmax[question] = answer
            elif len(answer) > 0:
                self.content[question] = answer
                # print  question+':'+answer


if __name__ == "__main__":
    starttime = time.time()
    url = "http://zhidao.baidu.com/search?{}&ie=gbk&site=-1&sites=0&date=0&pn={}0"
    food = gather_food(foodtype=foodtype).food_name()
    #with open('food.txt','r') as fp:
     #   f = json.load(fp)
    t = {'美食':['狗不理','羊肉泡馍','刀削面','兰州牛肉拉面']}
    content = fengjing(url, food).get_url()
    endtime = time.time()
    print 'all time', endtime - starttime