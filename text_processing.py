#coding:utf8

import os
import xlrd
from write_exal import writeexal


#marge all result
def marge_lt240xls():
    alldict ={}
    for dirpath,dirnames,dirfiles in os.walk('result'):
        for f in dirfiles:
            if not f.endswith('_lt240.xls'):
                continue
            dirname_file=os.path.join(dirpath,f)
            result = read_xls(dirname_file)
            for k,v in result.items():
                alldict[k] = v
            #print result
    writeexal(alldict,'all','result')
def read_xls(f):
    print f
    result_dict = {}
    workbook = xlrd.open_workbook(f)
    sheet = workbook.sheets()[0]
    nrows = sheet.nrows
    print nrows
    for i in range(nrows):
        question = sheet.cell(i,0).value
        answer = sheet.cell(i,1).value
        result_dict[question]=answer
    return result_dict
    workbook.close()
    
if __name__ =="__main__":
    marge_lt240xls()
