# -*- coding: utf-8 -*
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
import xlrd
import xml.etree.ElementTree as ET
import os

def get_content(hupu_url):
    headers={'User-agent':'Mozilla/5.0'}
    try:
        page=requests.get(hupu_url,headers=headers,timeout=3)
    except:
        return 'False',''
    content=page.text
    soup=BeautifulSoup(content,'lxml')
    title=soup.title
    #print(title.contents[0])
    bodys=soup.find_all(class_="artical-main-content")
    #print(bodys)
    time = soup.find('span', id = 'pubtime_baidu')
    #print(time.text)
    body=BeautifulSoup(str(bodys[0]),'lxml')
    tips=body.find_all("p")
    main_content=body.text
    #print(main_content)
    return [time.text.lstrip().rstrip(),hupu_url,title.contents[0],main_content]


sport_url_list = [
# NBA
"https://voice.hupu.com/nba/tag/2982", # 勇士
"https://voice.hupu.com/nba/tag/3023", # 骑士
"https://voice.hupu.com/nba/tag/811", # 火箭
"https://voice.hupu.com/nba/tag/2994", # 马刺
"https://voice.hupu.com/nba/tag/2987", # 雷霆
"https://voice.hupu.com/nba/tag/846", # 湖人
"https://voice.hupu.com/nba/tag/2698", # 热火
"https://voice.hupu.com/nba/tag/2990", # 森林狼
"https://voice.hupu.com/nba/tag/2985", # 老鹰
"https://voice.hupu.com/nba/tag/3027", # 太阳
"https://voice.hupu.com/nba/tag/3024", # 小牛
"https://voice.hupu.com/nba/tag/3021", # 鹈鹕
"https://voice.hupu.com/nba/tag/3033", # 魔术

# CBA
"https://voice.hupu.com/cba/tag/11907", # 广东
"https://voice.hupu.com/cba/tag/11868", # 北京
"https://voice.hupu.com/cba/tag/11926", # 辽宁
"https://voice.hupu.com/cba/tag/11852", # 新疆

# 中国足球
"https://voice.hupu.com/soccer/tag/496", # 英超
"https://voice.hupu.com/china/tag/11654", #恒大
"https://voice.hupu.com/china/tag/12136", # 上港
"https://voice.hupu.com/china/tag/11676", # 鲁能
"https://voice.hupu.com/china/tag/36301", # 苏宁
"https://voice.hupu.com/china/tag/11794", # 国安
"https://voice.hupu.com/china/tag/11633", # 申花
"https://voice.hupu.com/china/tag/36149", # 华夏幸福
"https://voice.hupu.com/china/tag/32947", # 河南建业
"https://voice.hupu.com/china/tag/11773", # 辽宁


# 国际足球
"https://voice.hupu.com/soccer/tag/2011", # 欧冠
"https://voice.hupu.com/soccer/tag/225", # 西甲
"https://voice.hupu.com/soccer/tag/1106", # 德甲
"https://voice.hupu.com/soccer/tag/700", # 意甲

# 羽毛球
"https://voice.hupu.com/sports/tag/9309"
]

i=0
# TODO: add sport list
k=0
doc_dir_path="./data/news/"
page_num=31
for sport_url in sport_url_list:
    sport_dir = doc_dir_path+"sport_"+str(k)+"/"
    isExists=os.path.exists(sport_dir)
    if not isExists:
        os.makedirs(sport_dir) 
    #os.makedirs(sport_dir)
    k = k + 1
    for j in range(1,page_num):
        page = j;
        min_body_len = 140
        #doc_dir_path="../data/news/"
        hupu = sport_url + '-%s.html' % (page)
        reslist = requests.get(hupu)
        reslist.encoding = 'utf-8'
        soup_list = BeautifulSoup(reslist.text, 'html.parser')
        news_pool=[]

        for news in soup_list.find_all('span',class_='n1'):
        #            print(news.text)
            hupu1 = news.find('a')
            url = hupu1.get('href')
            news_info = get_content(url)
            news_pool.append(news_info)

        for news in news_pool:
            body = news[3]
            if '//' in body:
                body = body[:body.index('//')]
            body = body.replace(" ", "")
            if len(body) <= min_body_len:
                continue

            doc = ET.Element("doc")
            ET.SubElement(doc, "id").text = "%d"%(i)
            ET.SubElement(doc, "url").text = news[1]
            ET.SubElement(doc, "title").text = news[2]
            ET.SubElement(doc, "datetime").text = news[0]
            ET.SubElement(doc, "body").text = body
            tree = ET.ElementTree(doc)
            tree.write(sport_dir + "%d.xml"%(i), encoding = "utf-8", xml_declaration = True)
            print(sport_dir + "%d.xml written"%(i))
            i += 1


print("The number of news: %d" % (i+1))

#             f = open('yingchao.txt', 'a', encoding='utf-8')
#             f.write(news.text)
#             f.close()

#title_dict = changeTitleToDict()
