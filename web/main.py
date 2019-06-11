#!congding = utf-8
__author__ = 'lcl'

from flask import Flask, render_template, request

from search_engine import SearchEngine
import traceback
import xml.etree.ElementTree as ET
import sqlite3
import configparser
import time

import jieba

app = Flask(__name__)

doc_dir_path = ''
db_path = ''
global page
global keys


def init():
    config = configparser.ConfigParser()
    config.read('../config.ini', 'utf-8')
    global dir_path, db_path
    dir_path = config['DEFAULT']['doc_dir_path']
    db_path = config['DEFAULT']['db_path']


@app.route('/')
def main():
    init()
    return render_template('home.html', error=True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods=['POST'])
def search():
    try:
        global keys
        global checked
        global dir_path
        checked = ['checked="true"', '', '']
        input_keys = request.form['key_word']
        select_keys1 = request.form['select_key1']
        select_keys2 = request.form['select_key2']
        
        keys = input_keys + "|" + select_keys1 + "%" + select_keys2
        #print(keys)
        if keys not in ['']:
            #print(time.clock())
            flag,page = searchidlist(input_keys, select_keys1, select_keys2)
            if flag==0:
                return render_template('search.html', input_key=input_keys, error=False)
            docs = cut_page(page, 0)
            #print(time.clock())
            
            return render_template('high_search.html', checked=checked, key=keys, input_key=input_keys, docs=docs, page=page,
                                   error=True)
        else:
            return render_template('search.html', error=False)

    except Exception as e:
        print('search error: ' + str(e))


def searchidlist(key, sport_type, world_range, selected=0):
    global page
    global doc_id
    se = SearchEngine('../config.ini', 'utf-8')
    flag, id_scores = se.search(key, sport_type, world_range, selected)
    # 返回docid列表
    doc_id = [i for i, s in id_scores]
    page = []
    for i in range(1, (len(doc_id) // 10 + 2)):
        page.append(i)
    return flag,page


def cut_page(page, no):
    docs = find(doc_id[no*10:page[no]*10])
    return docs


# 将需要的数据以字典形式打包传递给search函数
def find(docid, extra=False):
    docs = []
    global dir_path, db_path
    for id in docid:
        root = ET.parse(dir_path + '%s.xml' % id).getroot()
        url = root.find('url').text
        title = root.find('title').text
        body = root.find('body').text
        snippet = root.find('body').text[0:120] + '……'
        time = root.find('datetime').text.split(' ')[0]
        datetime = root.find('datetime').text
        doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': datetime, 'time': time, 'body': body,
               'id': id, 'extra': []}
        if extra:
            temp_doc = get_k_nearest(db_path, id)
            for i in temp_doc:
                root = ET.parse(dir_path + '%s.xml' % i).getroot()
                title = root.find('title').text
                doc['extra'].append({'id': i, 'title': title})
        docs.append(doc)
    return docs


@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page, (page_no-1))
        return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                               error=True)
    except:
        print('next error')


@app.route('/search/<key>/', methods=['POST'])
def high_search(key):
    try:
        selected = int(request.form['order'])
        for i in range(3):
            if i == selected:
                checked[i] = 'checked="true"'
            else:
                checked[i] = ''
        
        
        ks = key.split('|')
        key1 = ks[0]
        key2 = ks[1]
        #print(key2)
        select_key1 = key2.split('%')[0]
        #print(select_key1)
        select_key2 = key2.split('%')[1]
        #print("get: " +select_key1+ "%" +select_key2)
        flag,page = searchidlist(key1, select_key1, select_key2, selected)
        if flag==0:
            return render_template('search.html', error=False)
        docs = cut_page(page, 0)
        return render_template('high_search.html', checked=checked, key=keys, input_key=key1, docs=docs, page=page,
                                   error=True)
    except Exception as e:
        print('high search error: '+ str(e))


@app.route('/search/<id>/', methods=['GET', 'POST'])
def content(id):
    try:
        doc = find([id], extra=True)
        return render_template('content.html', doc=doc[0])
    except:
        print('content error')


def get_k_nearest(db_path, docid, k=5):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM knearest WHERE id=?", (docid,))
    docs = c.fetchone()
    #print(docs)
    conn.close()
    return docs[1: 1 + (k if k < 5 else 5)]  # max = 5


if __name__ == '__main__':
    jieba.initialize()  # 手动初始化（可选）
    app.run(host='0.0.0.0',port=5000)
