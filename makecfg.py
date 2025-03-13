def emptydir(dirname):  #清空資料夾
    if os.path.isdir(dirname):  #資料夾存在就刪除
        shutil.rmtree(dirname)
        sleep(2)  #需延遲,否則會出錯
    os.mkdir(dirname)  #建立資料夾

import glob
import os, shutil
from time import sleep
import random

batch = 24
subdivisions = 3
classname = ['none', 'bad', 'good']  #分類標籤
train = 'cfg/train.txt'  #訓練資料檔
valid = 'cfg/valid.txt'  #驗證資料檔
names = 'cfg/obj.names'  #分類標籤名稱檔
backup = 'cfg/weights'  #儲存訓練模型資料夾
validratio = 0.1  #驗證資料比例

print('開始建立設定資料！(第一次執行會較久，請耐心等候！)')
#下載預訓練檔

emptydir('cfg')  #建立設定資料夾
emptydir(backup)  #建立儲存訓練模型資料夾

#建立obj.data
# classes = len(classname)  #分類標籤數量
# f = open('cfg/obj.data', 'w')
# out = 'classes = ' + str(classes) + '\n'
# out += 'train = ' + train + '\n'
# out += 'valid = ' + valid + '\n'
# out += 'names = ' + names + '\n'
# out += 'backup = ' + backup + '\n'
# f.write(out)

#建立標籤檔obj.names
# f = open(names, 'w')
# out =''
# for cla in classname:
#     out += cla + '\n'
# f.write(out)

#建立訓練及驗證資料檔
imgfiles = glob.glob('product_label/*.jpg')  #讀取圖形檔
for i in range(len(imgfiles)):
    imgfiles[i] = imgfiles[i].replace('\\', '/')
validnum = int(len(imgfiles) * validratio)  #驗證資料數量
validlist = random.sample(imgfiles, validnum)  #取出驗證資料
f = open(valid, 'w')
out =''
for val in validlist:
    out += val + '\n'
f.write(out)
f = open(train, 'w')
out =''
for tra in imgfiles:
    if tra not in validlist:  #不是驗證資料的圖形資料
        out += tra + '\n'
f.write(out)

f.close()
print('建立設定資料完成！')
    
