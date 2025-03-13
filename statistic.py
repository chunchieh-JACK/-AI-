import time
import json

def detail(list1):
    with open("detail.json","r",encoding="utf-8") as DBB:
        readDB = json.load(DBB)

    with open("detail.json","w",encoding="utf-8") as DB:
        detail = {
            # "ID":"",
            "product":[],
            "time":""
        }
        temp = ""
        if len(list1) != 0:
            detail["product"] = list1
            detail["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            readDB["detail"].append(detail)
            json.dump(readDB, DB, ensure_ascii = False, indent = 4)      

def product_dict(list1):        
    with open("product_dict.json","r",encoding="utf-8") as RDICT:
        readDICT = json.load(RDICT)
    with open("product_dict.json","w",encoding="utf-8") as DICT:
        
        for i in list1:
            for j in readDICT["product_dict"]:
                for key,value in j.items():
                    if i == key:   
                        print("hello")
                        j[key] += 1
        json.dump(readDICT, DICT, ensure_ascii = False, indent = 4)
        
def readProduct():
        with open("product_dict.json","r",encoding="utf-8") as RDICT:
            readDICT = json.load(RDICT)
            return readDICT