# -*- coding: utf-8 -*
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
import xlrd
import xml.etree.ElementTree as ET

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
    return [time.text,hupu_url,title.contents[0],main_content]

i=0
# TODO: add sport list
for j in range(1,10):
    page = j;
    min_body_len = 140
    doc_dir_path="../data/news/"
    hupu = 'https://voice.hupu.com/soccer/tag/496-%s.html' % (page)
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
        tree.write(doc_dir_path + "%d.xml"%(i), encoding = "utf-8", xml_declaration = True)
        i += 1
            
print("page:")
print(j)
print("number:")
print(i)
            
            
            
#             f = open('yingchao.txt', 'a', encoding='utf-8')
#             f.write(news.text)
#             f.close()
 
#title_dict = changeTitleToDict()
