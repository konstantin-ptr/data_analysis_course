#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 23:53:33 2018

@author: konstantin
"""


import numpy as np
import pandas as pd
import re
import chardet
from collections import Counter
from scipy.spatial import distance

file_name='lines.txt'
preddict_line=0

#определяем кодировку файла
def predict_encoding(file_path, n_lines=20):
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
    return chardet.detect(rawdata)['encoding']

#считываем файл в список
txt_lists=[]
with open(file_name, encoding=predict_encoding(file_name)) as f:
    for line in f: 
        word_list=(re.split('[^a-zа-я0-9]',line.lower()))
        txt_lists.append(word_list)

#формируем словарь слов
t=[]
text_concur=[]
for n in range(len(txt_lists)):
    t=([x for x in txt_lists[n]])
    for i in range(len(t)):
        text_concur.append(t[i])
words_dict=dict(Counter([i for i in text_concur if len(i)>0]))

#создаем матрицу значений и заполняем ее
doc_array=np.zeros([len(txt_lists),len(words_dict)],dtype = int)
for i in range(len(txt_lists)):
    n=0
    for k in words_dict.keys():
        doc_array[i,n]=(txt_lists[i].count(k))
        n+=1

#считаем косинусное расстояние по матрице
v=list(map(lambda x: distance.cosine(doc_array[preddict_line],x),[doc_array[i] for i in range(doc_array.shape[0])]))
v=pd.DataFrame(v, columns=['Косинусное расстояние'])
v.sort_values(by='Косинусное расстояние', inplace=True)
print('Строке',preddict_line,'больше всего соответствуют:')
print(v[1:5])

