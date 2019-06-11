# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 16:30:40 2015

@author: bitjoy.net
"""

import jieba
import math
import operator
import sqlite3
import configparser
from datetime import *

class SearchEngine:
    stop_words = set()
    
    config_path = ''
    config_encoding = ''
    
    K1 = 0
    B = 0
    N = 0
    AVG_L = 0
    
    conn = None
    
    def __init__(self, config_path, config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        config = configparser.ConfigParser()
        config.read(config_path, config_encoding)
        f = open(config['DEFAULT']['stop_words_path'], encoding = config['DEFAULT']['stop_words_encoding'])
        words = f.read()
        self.stop_words = set(words.split('\n'))
        self.conn = sqlite3.connect(config['DEFAULT']['db_path'])
        self.K1 = float(config['DEFAULT']['k1'])
        self.B = float(config['DEFAULT']['b'])
        self.N = int(config['DEFAULT']['n'])
        self.AVG_L = float(config['DEFAULT']['avg_l'])
        

    def __del__(self):
        self.conn.close()
    
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
            
    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
        return n, cleaned_dict

    def fetch_from_db(self, term):
        c = self.conn.cursor()
        c.execute('SELECT * FROM postings WHERE term=?', (term,))
        return(c.fetchone())
    
    def use_and(self, sentence):
        # remove start and end spaces
        sentence = sentence.lstrip().rstrip()
        if not sentence:
            return False
        if sentence[0] == '(' and sentence[len(sentence)-1] == ')':
            return True
        else:
            return False

    def cond_result_by_BM25(self, sentence, sport_type, world_range):
        cond_keys = sport_type + " " + world_range
        # if not sport_type and not world_range:
        #     return result_by_BM25_time(sentence, time_start, time_end)
        cond_sores = self.BM25_And_Result(cond_keys)
        if self.use_and(sentence):
            print("Use and: " + sentence)
            sentence_scores = self.BM25_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            sentence_scores = self.score_by_BM25(sentence)
        BM25_scores = {}

        for key in cond_sores:
            if key in sentence_scores:
                BM25_scores[key] = sentence_scores[key] + cond_sores[key]

        BM25_scores = sorted(BM25_scores.items(), key = operator.itemgetter(1))
        BM25_scores.reverse()
        if len(BM25_scores) == 0:
            return 0, []
        else:
            return 1, BM25_scores  
    
    def cond_result_by_time(self, sentence, sport_type, world_range):
        cond_keys = sport_type + " " + world_range
        # if not sport_type and not world_range:
        #     return result_by_BM25_time(sentence, time_start, time_end)
        cond_sores = self.Time_And_Result(cond_keys)
        if self.use_and(sentence):
            print("Use and: " + sentence)
            sentence_scores = self.Time_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            sentence_scores = self.score_by_time(sentence)
        time_scores = {}
        for key in cond_sores:
            if key in sentence_scores:
                time_scores[key] = sentence_scores[key] + cond_sores[key]

        time_scores = sorted(time_scores.items(), key = operator.itemgetter(1))
        #time_scores.reverse()
        if len(time_scores) == 0:
            return 0, []
        else:
            return 1, time_scores                      

    def cond_result_by_hot(self, sentence, sport_type, world_range):
        cond_keys = sport_type + " " + world_range
        # if not sport_type and not world_range:
        #     return result_by_BM25_time(sentence, time_start, time_end)
        cond_sores = self.Hot_And_Result(cond_keys)
        if self.use_and(sentence):
            print("Use and: " + sentence)
            sentence_scores = self.Hot_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            sentence_scores = self.score_by_hot(sentence)
        hot_scores = {}
        
        for key in cond_sores:
            if key in sentence_scores:
                hot_scores[key] = sentence_scores[key] + cond_sores[key]

        hot_scores = sorted(hot_scores.items(), key = operator.itemgetter(1))
        hot_scores.reverse()
        if len(hot_scores) == 0:
            return 0, []
        else:
            return 1, hot_scores

    def score_by_BM25(self, sentence):
        # 按&分词, eg: 库里 & 格林
        # 把分词结果用结巴分词
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        BM25_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                s = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                if docid in BM25_scores:
                    BM25_scores[docid] = BM25_scores[docid] + s
                else:
                    BM25_scores[docid] = s
        return BM25_scores    
            
    def result_by_BM25(self, sentence):
        # 按&分词, eg: 库里 & 格林
        # 把分词结果用结巴分词
        if self.use_and(sentence):
            print("Use and: " + sentence)
            BM25_scores = self.BM25_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            BM25_scores = self.score_by_BM25(sentence)

        BM25_scores = sorted(BM25_scores.items(), key = operator.itemgetter(1))
        BM25_scores.reverse()
        if len(BM25_scores) == 0:
            return 0, []
        else:
            return 1, BM25_scores
    
    
    def result_by_time(self, sentence):
        if self.use_and(sentence):
            print("Use and: " + sentence)
            time_scores = self.Time_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            time_scores = self.score_by_time(sentence)
        time_scores = sorted(time_scores.items(), key = operator.itemgetter(1))
        if len(time_scores) == 0:
            return 0, []
        else:
            return 1, time_scores

    def score_by_time(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        time_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                if docid in time_scores:
                    continue
                news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime
                docid = int(docid)
                td = (timedelta.total_seconds(td) / 3600) # hour
                time_scores[docid] = td
        
        return time_scores
    
    def result_by_hot(self, sentence):
        if self.use_and(sentence):
            print("Use and: " + sentence)
            hot_scores = self.Hot_And_Result(sentence)
        else:
            print("Use or: " + sentence)
            hot_scores = self.score_by_hot(sentence)
        hot_scores = sorted(hot_scores.items(), key = operator.itemgetter(1))
        hot_scores.reverse()
        if len(hot_scores) == 0:
            return 0, []
        else:
            return 1, hot_scores

    def score_by_hot(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        hot_scores = {}
        for term in cleaned_dict.keys():
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime
                BM25_score = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                td = (timedelta.total_seconds(td) / 3600) # hour
                hot_score = math.log(BM25_score) + 1 / td
                if docid in hot_scores:
                    hot_scores[docid] = hot_scores[docid] + hot_score
                else:
                    hot_scores[docid] = hot_score
        
        return hot_scores

    def result_by_BM25_and(self, sentence):
        BM25_scores = self.BM25_And_Result(sentence)
        BM25_scores = sorted(BM25_scores.items(), key = operator.itemgetter(1))
        BM25_scores.reverse()
        if len(BM25_scores) == 0:
            return 0, []
        else:
            return 1, BM25_scores
    
    def result_by_time_and(self, sentence):
        time_scores = self.Time_And_Result(sentence)
        time_scores = sorted(time_scores.items(), key = operator.itemgetter(1))
        if len(time_scores) == 0:
            return 0, []
        else:
            return 1, time_scores

    def result_by_hot_and(self, sentence):
        hot_scores = self.Hot_And_Result(sentence)
        hot_scores = sorted(hot_scores.items(), key = operator.itemgetter(1))
        if len(hot_scores) == 0:
            return 0, []
        else:
            return 1, hot_scores

    def BM25_And_Result(self, sentence):
        # 按&分词, eg: 库里 & 格林
        # 把分词结果用结巴分词
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        BM25_scores = {}
        And_result = {}
        count = 0
        for term in cleaned_dict.keys():  
            #print(term)
            And_result.clear()    
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                s = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                if docid in BM25_scores:
                    BM25_scores[docid] = BM25_scores[docid] + s
                    And_result[docid] = BM25_scores[docid]
                else:
                    if not count:
                        BM25_scores[docid] = s
            if count:
                BM25_scores.clear()
                BM25_scores = And_result.copy()
            count+=1
            # And_result.clear()
        return BM25_scores
        
    def Time_And_Result(self, sentence):
        # 按&分词, eg: 库里 & 格林
        # 把分词结果用结巴分词
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        time_scores = {}
        And_result = {}
        count = 0
        for term in cleaned_dict.keys():  
            #print(term)
            And_result.clear()    
            r = self.fetch_from_db(term)
            if r is None:
                continue
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                if docid in time_scores:
                    continue
                news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime
                docid = int(docid)
                td = (timedelta.total_seconds(td) / 3600) # hour
                if docid in time_scores:
                    # BM25_scores[docid] = BM25_scores[docid] + s
                    And_result[docid] = td
                else:
                    if not count:
                        time_scores[docid] = td
            if count:
                time_scores.clear()
                time_scores = And_result.copy()
            count+=1
            # And_result.clear()
        return time_scores

    def Hot_And_Result(self, sentence):
        seg_list = jieba.lcut(sentence, cut_all=False)
        n, cleaned_dict = self.clean_list(seg_list)
        hot_scores = {}
        And_result = {}
        count = 0
        for term in cleaned_dict.keys():  
            #print(term)
            And_result.clear()    
            r = self.fetch_from_db(term)
            if r is None:
                continue
            df = r[1]
            w = math.log2((self.N - df + 0.5) / (df + 0.5))
            docs = r[2].split('\n')
            for doc in docs:
                docid, date_time, tf, ld = doc.split('\t')
                docid = int(docid)
                tf = int(tf)
                ld = int(ld)
                news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                now_datetime = datetime.now()
                td = now_datetime - news_datetime
                BM25_score = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
                td = (timedelta.total_seconds(td) / 3600) # hour
                hot_score = math.log(BM25_score) + 1 / td
                if docid in hot_scores:
                    hot_scores[docid] = hot_scores[docid] + hot_score
                    And_result[docid] = hot_scores[docid]
                else:
                    if not count:
                        hot_scores[docid] = hot_score
            if count:
                hot_scores.clear()
                hot_scores = And_result.copy()
            count+=1
            # And_result.clear()
        return hot_scores

    def search(self, sentence, sport_type, world_range, sort_type = 0):
        print("Call search...")
        print("Order " + str(sort_type), end=";")
        if sort_type == 0:
            if not sport_type and not world_range:
                print("No conds", end=";")
                return self.result_by_BM25(sentence)
            else:
                print("Use conds: " + sport_type + world_range, end=";")
                return self.cond_result_by_BM25(sentence, sport_type, world_range)
        elif sort_type == 1:
            if not sport_type and not world_range:
                print("No conds", end=";")
                return self.result_by_time(sentence)
            else:
                print("Use conds: " + sport_type + world_range, end=";")
                return self.cond_result_by_time(sentence, sport_type, world_range)
        elif sort_type == 2:
            if not sport_type and not world_range:
                print("No conds", end=";")
                return self.result_by_hot(sentence)
            else:
                print("Use conds: " + sport_type + world_range, end=";")
                return self.cond_result_by_hot(sentence, sport_type, world_range)

if __name__ == "__main__":
    se = SearchEngine('../config.ini', 'utf-8')
    flag, rs1 = se.result_by_BM25('格林 库里 考辛斯 武当松柏 德雷蒙德')
    print("Or Result Number: " + str(len(rs1)))
    flag, rs2 = se.result_by_BM25_and('库里 足球')
    print("And Result Number: " + str(len(rs2)))
    flag, rs3 = se.cond_result_by_BM25('库里', '足球', '国内')
    print("Cond Result Number: " + str(len(rs3)))
    flag, rs4 = se.result_by_time_and('库里 足球')
    print("Time And Result: ", str(len(rs4)))
    flag, rs5 = se.result_by_hot_and('库里 足球')
    print("Time And Result: ", str(len(rs5)))
    print("Use and: "+ str(se.use_and("(库里)")))
    print("Not use and: "+ str(se.use_and("库里 格林")))
    
    # flag, rs1 = se.search('库里', 0)
    # flag, rs2 = se.search('格林', 0)
    # rs1ids = [item[0] for item in rs1]
    # rs2ids = [item[0] for item in rs2]
    # rsids = sorted(list(set(rs1ids) & set(rs2ids)))
    # #print(list(rs3)[:10])
    # print(rsids)