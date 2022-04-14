#!/usr/bin/env python
import os,re,datetime
import pandas as pd

from unicodedata import name
from paddleocr import PaddleOCR

#-----------------------------input------------------------------
#本轮开始检测的时间, eg: start_time = "2022-04-06"
# start_time = "2022-04-07"
#本轮周期为几天(整数), eg: period = 5
period = 5
#存放图片的文件夹目录, eg: pict_path = "/Users/joy/Downloads/本科生 2018级 3班核酸检测报告" 
# pict_path = "/Users/joy/Downloads/本科生 2018级 3班核酸检测报告" 
pict_path = "./pictures"
#学号-姓名的excel文件路径, eg: data_path = "/Users/joy/Downloads/2018级名单.xlsx"
# data_path = "."
#输出文件的路径, eg: out_file_path = "./out.xlsx"
# out_file_path = "./out.xlsx"

#----------------------------------------------------------------

class OCR(object):
    '''
    虚基类
    '''
    def __init__(self,):
        #判断ocr是否可靠
        self.flag = True
    def ocr(self,img_path):
        ocr = PaddleOCR(lang='ch') # 第一次运行需要下载模型
        self.result = ocr.ocr(img_path)
    
    def setPictPath(self,path):
        self.pict_path = path

    def setOutfilePath(self,path):
        self.out_file_path = path
    
    def setDataPath(self,path):
        self.data_path = path

    def witein(self):
        pass
    def mainprocess(self):
        pass
    

class natOCR(OCR):
    '''
    核酸检测OCR子类,判断是否有在一段时间内做过核酸
    '''
    #输入起始日期与间隔
    def __init__(self,start_time,delta_days):
        super().__init__()
        self.start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
        delta = datetime.timedelta(days=delta_days)
        self.end_time = self.start_time + delta

        #判断process1的精度
        self.flag = True
        #判断process2的精度
        self.flag2_name = True
        self.falg2_time = True
    
    def mainprocess(self,):
        for picture_name in os.listdir(self.pict_path):
            #重制flag
            self.flag = True
            self.flag2_name = True
            self.flag2_time = True
            #如果是图片
            if picture_name.lower().endswith(".jpg")\
                 or picture_name.lower().endswith(".png"):
                
                #ocr
                self.ocr(
                    os.path.join(
                        self.pict_path,picture_name
                    )
                )
                #如果process2比较粗糙的处理没有成功，则使用process1
                if not self.process2():
                    self.process1(picture_name)
                self.writein()


            
    def getIdNameIdx1(self):
        #定位身份证
        self.id_idx = -1
        #定位第一次'姓名'
        self.name_idx = -1

        self.flag  = True

        for i in range(len(self.result)):
            #寻找身份证索引
            if "身份证" in self.result[i][-1][0]:
                self.id_idx = i
            #寻找第一次姓名索引
            if "姓名" in self.result[i][-1][0]:
                self.name_idx = i
            if self.name_idx != -1:
                break
        if self.name_idx - self.id_idx > 7:
            self.flag = False
            print("OCR有问题")

        return self.flag

    def getName1(self):
        #采样者姓名
        self.sampling_name = ''
        #判断姓名的识别程精度
        if self.result[self.name_idx+1][-1][-1] > 0.9:
            self.sampling_name = self.result[self.name_idx+1][-1][0]
        else:
            self.flag = False
        

    
    def getTime1(self):
        #采样时间
        self.sampling_time = ''

        #判断是否是'采样时间'，最多允许一个位置偏差
        for i in range(self.name_idx+3,self.name_idx+10):
            if "时间" in  self.result[i][-1][0]:
                #正则表达式搜索采样时间
                pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
                
                #判断时间是否包含在内
                sampling_time_search = re.search(pattern,self.result[i][-1][0])
                #如果在则时间索引即为i
                if sampling_time_search:
                    time_idx = i
                #如果不在就在i+1，不考虑除了这两种情况以外的情况
                else:
                    time_idx = i+1
                    sampling_time_search = re.search(pattern,self.result[time_idx][-1][0])
                #判断采样时间识别精度
                try:
                    if self.result[time_idx][-1][-1] > 0.9:
                        self.sampling_time = sampling_time_search.group()
                    else:
                        self.flag = False
                except:    
                    self.flag = False


                break    
        else:
            self.flag = False
            print("OCR有问题")

    def judge(self,):
        try:
            now_time = datetime.datetime.strptime(self.sampling_time,'%Y-%m-%d')
            if self.start_time <now_time< self.end_time:
                return "是"
            else:
                return "否"
        except:
            return ''

    def setDataPath(self,path):
        self.data_path = path
        self.df = pd.read_excel(path)

    def getStuId(self,):
        try:
            id = self.df.loc[self.df['姓名']==self.sampling_name].iloc[0,1]
            return id
        except:
            return -1


    def writein(self):

        data = [["物理学院",self.getStuId(),self.sampling_name,self.judge(),' ',self.sampling_time]]
        df1 = pd.DataFrame(data,columns = ['院系','学号','姓名','是否检测','如未检测，请说明原因','采样时间'])

        try:
            df_append = pd.read_excel(self.out_file_path)
            df_append = df_append.append(df1)
            df_append.to_excel(self.out_file_path,index=False)
        except:
            df1.to_excel(self.out_file_path,index=False)
    
    def process1(self,picture_name):
        if self.getIdNameIdx1():
            if self.flag2_name == False:
                self.getName1()
            if self.flag2_time == False:
                self.getTime1()                   
        if self.flag == False:
            self.sampling_name = picture_name
            self.sampling_time = ''
        return self.flag
    
    def getName2(self):
        pattern = re.compile(r"\('姓名.',.\d*.\d*\).*?\('(.*?)',")

        name_lst = re.findall(pattern,str(self.result))
        name_lst = [name.strip() for name in name_lst]

        if len(set(name_lst)) == 1:
            self.sampling_name = name_lst[0]
        else:
            self.flag2_name = False
        return self.flag2_name

    def getTime2(self):
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        time_lst = re.findall(pattern,str(self.result))

        if len(time_lst) == 3:
            self.sampling_time = time_lst[0]
        else:
            self.flag2_time = False
        return self.flag2_time

    def process2(self,):
        self.getName2()
        self.getTime2()
        return self.flag2_name and self.flag2_time
            

def getStartTime():
    file_lst = os.listdir(".")
    for item in file_lst:
        if item.endswith(".time"):
            return  item.split(".")[0]


def getDataPath():
    file_lst = os.listdir(".")
    for item in file_lst:
        if item.endswith(".xlsx") and "output_file" not in item:
            return  item

if __name__ == '__main__':
    #切换工作路径为改.py文件目录
    #os.chdir(os.path.dirname(__file__))
    start_time = getStartTime()
    out_file_path = "./output_file-"
    out_file_path += datetime.datetime.now().strftime("%H%M%S")
    out_file_path += ".xlsx"
    
    data_path = getDataPath()

    ocr = natOCR(start_time,period)
    ocr.setDataPath(data_path)
    ocr.setOutfilePath(out_file_path)
    ocr.setPictPath(pict_path)
    ocr.mainprocess()

