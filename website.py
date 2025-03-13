# -*- coding: utf-8 -*-#
#导入flask类库，render_template模板，
from flask import Flask, render_template, request, jsonify, make_response,Response
#安全文件名
from werkzeug.utils import secure_filename
import os
import cv2
from PIL import Image
from io import BytesIO
import numpy as np
from datetime import timedelta
import yolov4
from cgitb import reset
import shutil
import collections
from statistic import *
# import arduino

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/",
    template_folder="./templates"
)
# COM_PORT = 'COM3'   
# BAUD_RATES = 9600   
# ser = serial.Serial(COM_PORT, BAUD_RATES) 
num = 1 
cap = cv2.VideoCapture(0)
def get_frames():
    flag = 1 
    global num
    while(cap.isOpened()):
        ret_flag, Vshow = cap.read() 
        cv2.imshow("Capture_Test",Vshow)  #視窗顯示，顯示名為 Capture_Test
        k = cv2.waitKey(1) & 0xFF #每幀資料延時 1ms，延時不能為 0，否則讀取的結果會是靜態幀
        if k == ord('s'):  #若檢測到按鍵 ‘s’，列印字串
            cv2.imwrite("images/"+ str(num) + ".jpg", Vshow)
            print(cap.get(3)) #得到長寬
            print(cap.get(4))
            print("success to save"+str(num)+".jpg")
            print("-------------------------")
            num += 1
        elif k == ord('q'): #若檢測到按鍵 ‘q’，退出
            break
    cap.release() #釋放攝像頭
    cv2.destroyAllWindows()#刪除建立的全部視窗

pic_count = 0 #全域宣告辯識次數
@app.route('/prediction', methods=['POST', 'GET'])
def upload():
    #print(request.method)
    DICT = []
    global pic_count #全域宣告辯識次數
    if request.method == 'POST':
        if request.values['send'] == '辨識':
            pic_count = pic_count + 1 #辨識次數
            #print(pic_count)
            lab, img = yolov4.yolo_detect(img_path='images/'+ str(pic_count) + '.jpg')
            for i in range(len(lab)):
                products(lab[i][0])
                #print(lab[i][0])
            #print(things_list)
            # data_raw = ser.readline()  
            # weight = data_raw.decode()
            # print(weight)
            cv2.imwrite('out/' + str(pic_count) + '_res.jpg', img)
            return render_template('project2.html',list1 = things_list, picture_ped = '.out/' + 'pictures_'+ str(pic_count) +'_res.jpg', product_dict=readProduct())      
    return render_template('project.html')

things_list = []
def products(things):
    things_list.append(things)
    print(things_list)

    
@app.route('/video')
def video():
    return Response(get_frames())

@app.route('/account', methods=['GET', 'POST'])
def account():
    global pic_count
    global num
    finish = "finish" 
    shutil.rmtree('out')
    shutil.rmtree('images')
    os.mkdir("out")
    os.mkdir("images")
    pic_count = 0
    num = 1
    name=""
    weight=0
    number=0
    i=0
    j=0
    count_1 = 0
    D={'rice_ball':28,'instant_noodles':50,'black_tea':10,'ovaltine':25,'oreo':40,'cheetos':30,'ferrero_rocher':16,'puff':36,'coke':25,'pocky':33,'pudding':12,'yogurt_drink':49,'matcha_latte':35}
    repeat = []                           # 新增 repeat 變數為空串列
    list1 = []
    list2 = []
    list3 = []
    total = 0

    for i in things_list:                        # 使用 for 迴圈，依序取出每個字元
        d3 = collections.Counter(things_list)
        if d3[i] >= 1 and i not in  list1:         # 如果次數大於 1，且沒有存在 repeat 串列中
            list1.append(i)
    print(list1)
    for i in range(len(list1)):
        a = D[list1[i]] * d3[list1[i]]
        total = total + a
        list3.append(a)
        list2.append(d3[list1[i]])
        #print(list3[i])
        print(D[list1[i]])
        print(d3[list1[i]])
        print(D[list1[i]] * d3[list1[i]])
        print(list3)
        detail(list1)           # 統計商品
        product_dict(list1)
        
           
    things_list.clear()
    return render_template("project2.html", list1=list1, list2=list2, list3=list3, total=total, product_dict=readProduct())

@app.route('/check_account', methods=['GET', 'POST'])
def check_account():
    list1 = []
    list2 = []
    list3 = []
    total=0
    return render_template("project2.html", list1=list1, list2=list2, list3=list3, total=total, product_dict=readProduct())

@app.route("/")
def index():
    list1=[]
    list2=[]
    list3=[]
    total=0
    # while True:
    #     while ser.in_waiting:         
    #         data_raw = ser.readline()
    #         weight = data_raw.decode()
    #         print(weight)
    #     return render_template("project2.html",list1=list1,list2=list2,list3=list3,wei=weight)
    
    return render_template("project2.html", list1=list1, list2=list2, list3=list3, total=total, product_dict=readProduct())


if __name__ == '__main__':
    app.run(port=5000, debug=True)