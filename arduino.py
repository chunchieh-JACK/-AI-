from cgitb import reset
from logging import exception
from flask import Flask
from flask import request
from flask import render_template
from flask import Response
import cv2
import serial
app=Flask(
    __name__,
    static_folder="static",
    static_url_path="/",
    template_folder="./templates"
)
COM_PORT = 'COM3'   
BAUD_RATES = 9600   
ser = serial.Serial(COM_PORT, BAUD_RATES) 
cap = cv2.VideoCapture(0)
def get_frames():
    flag = 1 
    num = 1 
    cap = cv2.VideoCapture(0)
    while(cap.isOpened()):
        ret_flag, Vshow = cap.read() 
        cv2.imshow("Capture_Test",Vshow)  #視窗顯示，顯示名為 Capture_Test
        k = cv2.waitKey(1) & 0xFF #每幀資料延時 1ms，延時不能為 0，否則讀取的結果會是靜態幀
        if k == ord('s'):  #若檢測到按鍵 ‘s’，列印字串
            cv2.imwrite("D:/"+ str(num) + ".jpg", Vshow)
            print(cap.get(3)) #得到長寬
            print(cap.get(4))
            print("success to save"+str(num)+".jpg")
            print("-------------------------")
            num += 1
        elif k == ord('q'): #若檢測到按鍵 ‘q’，退出
            break
    cap.release() #釋放攝像頭
    cv2.destroyAllWindows()#刪
@app.route('/video')
def video():
    return Response(get_frames())  
@app.route("/")
def index():
    weight=0
    try:
        while True:
            while ser.in_waiting:         
                data_raw = ser.readline()  
                weight = data_raw.decode()
            return render_template("project.html",wei=weight)
    except KeyboardInterrupt:
        ser.close()
        print("88")
    

app.run(port=3000)