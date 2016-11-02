#!/usr/bin/env python 
#coding:utf-8

import xlwt


def writeexal(n,name='result',i=240):

    book = xlwt.Workbook(encoding='gbk')
    sheet = book.add_sheet('result',cell_overwrite_ok=True)
    row = 0
    for k,v in n.items():
        sheet.write(row,0,k)
        sheet.write(row,1,v)
        row +=1
    book.save('result/%s_%s.xls'%(name,i))
