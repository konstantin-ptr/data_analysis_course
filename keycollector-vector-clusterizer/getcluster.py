# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 10:55:39 2018

@author: user
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import progressbar
import os, glob


def predict_encoding(file_path, n_lines=20):
    '''Predict a file encoding using chardet'''
    import chardet

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

def predict_sep(file_path, s, n_lines=20):
    '''Predict a file encoding using chardet'''
    import chardet,csv

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        lines=[0, 30] # диапазон строк
        f=open(file_path,encoding=s)
        i=0
        for line in f:
            if i in lines:
                i+=1
        dl=csv.Sniffer().sniff(line).delimiter
    return dl


list_csv = [i for i in glob.glob('*.{}'.format("csv"))]

if(len(list_csv)>1):
    for i in range(len(list_csv)):
        print(i,list_csv[i])
    kon_file=list_csv[int(input('Выберите файл с URL конкуретов: '))]
    words_file=list_csv[int(input('Выберите файл с частотами: '))]
else:
    print('Файлов в дирректории недостаточно')


kon=pd.read_csv(str(kon_file), sep=predict_sep(kon_file,predict_encoding(kon_file)),encoding=predict_encoding(kon_file),header='infer',index_col=False)
words=pd.read_csv(words_file,sep=predict_sep(words_file,predict_encoding(words_file)),encoding=predict_encoding(words_file),header='infer',index_col=False)


os.system('cls')




if(len(kon.columns)>1):
    print("В файле конкурентов с URL найдено",len(kon.columns),"колонок")
    for i in range(len(kon.columns)):
        print(i,kon.columns[i])
    kon_phrase=kon.columns[int(input('Выберите колонку с фразами: '))]
    kon_url=kon.columns[int(input('Выберите колонку с URL: '))]
else:
    print('Колонок слишком мало')
    

    
os.system('cls')
if(len(words.columns)>2):
    print("В файле фраз [YW] найдено",len(kon.columns),"колонок")
    for i in range(len(words.columns)):
        print(i,words.columns[i])       
    words_phrase=words.columns[int(input('Выберите колонку с фразами: '))]
    words_base=words.columns[int(input('Выберите колонку с Базовыми частотами [YW]: '))]
    words_accur=words.columns[int(input('Выберите колонку с !Точными !частотами [YW]: '))]
else:
    print('Колонок слишком мало')

os.system('cls')
print("Методы кластеризации:\n0 по частотам\n1 по фразам")
words_method=int(input('Ваш выбор: '))


if(words_method==1):
       for i in range(len(words.columns)):
              print(i,words.columns[i])
       words_col_cls=words.columns[int(input('Выберите колонку с помеченными фразами кластеров: '))]
else:
       min_accur=int(input("[Частота ! [YW]] от которой разбивать на кластер: "))


#если напортачили в excel то затираем
#kon = kon.loc[~kon[kon_phrase].isin(['#ИМЯ?'])]
#words = words.loc[~words['Фраза'].isin(['#ИМЯ?'])]
                  
#добавили поле позиций и частот во фрем конкуретов                  
kon['pos']=None



#собрали уникальные фразы конкурентов, проставили позиции и потерли лишнее
kon_uniq=pd.Series(pd.unique(kon[kon_phrase]))
bar = progressbar.ProgressBar(max_value=len(kon_uniq))
os.system('cls')
print('\n\nРасставляю позиции')
for kon_i in range(len(kon_uniq)):
    kon_uniq_df=kon[kon[kon_phrase]==kon_uniq[kon_i]].copy()
    kon_uniq_df.pos=range(1,len(kon_uniq_df)+1)
    kon.loc[kon_uniq_df.index]=kon_uniq_df 
    bar.update(kon_i+1)
del(kon_i,kon_uniq_df,bar)
kon=kon[kon['pos']<51]
kon=kon.sort_values(by=['pos'], ascending=True)
#собрали актуальные уникаьлные фразы
kon_uniq=pd.Series(pd.unique(kon[kon_phrase]))
words_uniq=pd.Series(pd.unique(words[words_phrase]))

#проставляем в таблице конкурентов частоты
kon=kon.join(words.set_index(words_phrase), on=words_phrase,lsuffix='_left', rsuffix='_right')[[kon_phrase,kon_url, 'pos', words_base, words_accur]]









if(words_method==1):
       #создаем список нужных слов по которым будем собирать кластеры на основе отмеченных
       kon_uniq_limit=pd.Series( pd.unique(words[words[words_col_cls].notnull()][kon_phrase] ))
       #собрали все фразы внутреннего круга итерации вычев интерационные
       kon_uniq_ins=pd.Series(list(set(pd.Series(pd.unique(kon[kon_phrase])))-set(kon_uniq_limit)))   
else:
       #создаем список нужных слов по которым будем собирать кластеры
       kon_uniq_limit=pd.Series( pd.unique(kon[kon[words_accur]>=min_accur][kon_phrase]) )
       #kon.drop(['Базовая частота [YW]','Частота "!" [YW]'], inplace=True, axis=1)
       #собрали все фразы внутреннего круга итерации
       kon_uniq_ins=pd.Series(pd.unique(kon[kon[words_accur]<min_accur][kon_phrase]))
       kon_uniq_limit=kon_uniq_limit.reset_index(drop=True)










#функция простановки коэфициентов по позициям
def get_k(pos):
    pos[(0<pos)&(pos<4)]=0.1
    pos[(3<pos)&(pos<11)]=0.05
    pos[(10<pos)&(pos<31)]=0.015
    pos[(30<pos)&(pos<51)]=0.001
    pos[50<pos]=0.0
    return pos
    
    
    
df_final=pd.DataFrame(columns=[words_phrase, 'Релевантная','k'])

print('\n\nКластеризую')
bar = progressbar.ProgressBar(max_value=len(kon_uniq_limit))
#бегаем по ключам по которым нужно собрать кластеры 
for kon_i in range(len(kon_uniq_limit)):
    #выборка верхнего уровня
    df=kon[kon[kon_phrase]==kon_uniq_limit[kon_i]]
    df=df.sort_values(by=['pos'], ascending=True)
    df=df.drop_duplicates(subset=kon_url, keep='first', inplace=False)
    
    #внутренний круг
    for kon_ins_i in range(len(kon_uniq_ins)):  
        #выборка внутренней фразы
        df1=kon[kon[kon_phrase]==kon_uniq_ins[kon_ins_i]]
        df1=df1.sort_values(by=['pos'], ascending=True)
        df1=df1.drop_duplicates(subset=kon_url, keep='first', inplace=False)
        
        #пересечения
        df2=df.merge(df1, on=kon_url, how='inner')
        if(len(df2)):
            df2=df2.rename(columns={'pos_x':'k_x','pos_y':'k_y'})
            k=sum(get_k(df2['k_x'].copy())+get_k(df2['k_y'].copy()))/2
            df_final.loc[len(df_final)]=(kon_uniq_limit[kon_i],kon_uniq_ins[kon_ins_i],k)
    bar.update(kon_i+1)
del(bar,kon_i,kon_ins_i,k,df,df1,df2)



#добавляем частоты
df_final=df_final.join(words.set_index(words_phrase), on='Релевантная')[[words_phrase, 'Релевантная','k',words_base,words_accur]]


#сохраняем, если файл открыт, то меняем путь
def to_xls(f):
       try:
              writer = pd.ExcelWriter(f)
              df_final.sort_values([kon_phrase,'k'], ascending=[1,0]).to_excel(writer,'All')
              df_final[df_final['k']>0.29].sort_values([kon_phrase,'k'], ascending=[1,0]).to_excel(writer,'Top >0.3')
              df_final[df_final['k']<0.29].sort_values([kon_phrase,'k'], ascending=[1,0]).to_excel(writer,'Low <0.3')
              writer.save()
              print('\n\nСохранил в', f)
       except (PermissionError,OSError,UnboundLocalError):
              file=input("\n\nНет доступа!\n\nПапка для сохранения: ")
              file=file+file_name
              to_xls(file)
file_name="df_final.xlsx"
to_xls(file_name)   