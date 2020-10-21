import requests
import re
import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
from itertools import chain



news_path='Total_news.csv'

#Line notify
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.text

token=''
def lineNotifyFile(token, msg,path):
    headers = {
        "Authorization": "Bearer " + token, 
    }
    file={'imageFile':open(path,'rb')}
    payload = {'message': '\n'+format(datetime.datetime.now(),'%Y-%m-%d')+msg+'\n'}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, 
                  params = payload,
                  files=file)



#製造時間區間，格式為%Y/%m/%d
def produce_d_interval(st,ed):
    rs=[]
    temp1=datetime.datetime.strptime(st,'%Y/%m/%d')
    temp2=datetime.datetime.strptime(ed,'%Y/%m/%d')
    while temp2-temp1>=datetime.timedelta(days=0):
        rs.append(datetime.datetime.strftime(temp1,'%Y/%m/%d'))
        temp1=temp1+datetime.timedelta(days=1)
    return rs

end_date=datetime.datetime.now()
start_date=end_date-datetime.timedelta(days=1)


def grab_day(x):
    try:
        return re.sub(string=re.search(string=x,pattern='\d{4}-\d{2}-\d{2}').group(0),pattern='-',repl='/')
    except:
        return ''



D=pd.read_csv(news_path,encoding='utf_8_sig')

#去除null content，程式還是有不完美的地方
D=D[~D.content.isnull()]
D=D[~D.duplicated(subset=['author','title','Source','dt_publish'])]
D['date']=D.dt_publish.map(grab_day)



def news_notify(start_date,end_date,D,Source):
    #read all data in restricted time interval
    if end_date-start_date>datetime.timedelta(days=1):
        temp_e=format(end_date,'%Y/%m/%d')
        temp_s=format(start_date,'%Y/%m/%d')
        time_interval=produce_d_interval(st=temp_s,ed=temp_e)
    else:
        time_interval=[format(end_date,'%Y/%m/%d')]
    D_old=pd.read_csv('old_news.csv',encoding='utf_8_sig')
    D=D[D['date'].isin(time_interval)]
    D=D.iloc[[i for i,j in enumerate(D.url) if j not in D_old.url.values],:]
    if D.shape[0] == 0:
        return 'Done'
    #看看Source是不是None，不然推播想要看的新聞來源
    if Source is not None:
        T=D[D.Source == Source]
        T.to_csv('C:/Users/lenovon/Desktop/Test/old_news.csv',encoding='utf_8_sig',index=0,mode='a',header=0)
        for i in range(0,T.shape[0]):
            lineNotifyMessage(token,'\n'+T.dt_publish.iloc[i]+':'+T.title.iloc[i])
            if len(T.content.iloc[i])>1500 and len(T.content.iloc[i])<3000:
                lineNotifyMessage(token,'\n'+T.content.iloc[i][0:1500])
                lineNotifyMessage(token,'\n'+T.content.iloc[i][1500:])
            elif len(T.content.iloc[i])>3000:
                lineNotifyMessage(token,'\n'+T.content.iloc[i][0:1500])
                lineNotifyMessage(token,'\n'+T.content.iloc[i][1500:3000])
                lineNotifyMessage(token,'\n'+T.content.iloc[i][3000:])
            else:
                lineNotifyMessage(token,'\n'+T.content.iloc[i])


news_notify(start_date=start_date,end_date=end_date,D=D,Source='iThome')






