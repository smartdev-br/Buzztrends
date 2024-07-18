#!/usr/bin/env python
# -*- Coding: UTF-8 -*-

__author = 'Eduardo S. Pereira'
__data = '20/05/2016'

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import metrics
from numpy import array, where
from numpy.core.defchararray import lower, replace, strip, join, split
from sklearn.externals import joblib
import csv
import os
import re
from unicodedata import normalize



pt_stopwords = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para',
                    'e', 'com', 'nao', 'uma', 'os', 'no', 'se', 'na', 'por',
                    'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele',
                    'das', 'tem', 'a', 'seu', 'sua', 'ou', 'ser', 'quando',
                    'muito', 'ha', 'nos', 'ja', 'esta', 'eu', 'tambem', 'so',
                    'pelo', 'pela', 'ate', 'isso', 'ela', 'entre', 'era',
                    'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem',
                    'nas', 'me', 'esse', 'eles', 'estao', 'voce', 'tinha',
                    'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'as',
                    'minha', 'tem', 'numa', 'pelos', 'elas', 'havia', 'seja',
                    'qual', 'sera', 'nos', 'tenho', 'lhe', 'deles', 'essas',
                    'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te',
                    'voces', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua',
                    'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas',
                    'dela', 'delas', 'esta', 'estes', 'estas', 'aquele',
                    'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou',
                    'esta', 'estamos', 'estao', 'estive', 'esteve', 'estivemos',
                    'estiveram', 'estava', 'estavamos', 'estavam', 'estivera',
                    'estiveramos', 'esteja', 'estejamos', 'estejam',
                    'estivesse', 'estivessemos', 'estivessem', 'estiver',
                    'estivermos', 'estiverem', 'hei', 'ha', 'havemos',
                    'hao', 'houve', 'houvemos', 'houveram', 'houvera',
                    'houveramos', 'haja', 'hajamos', 'hajam', 'houvesse',
                    'houvessemos', 'houvessem', 'houver', 'houvermos',
                    'houverem', 'houverei', 'houvera', 'houveremos',
                    'houverao', 'houveria', 'houveriamos', 'houveriam',
                    'sou', 'somos', 'sao', 'era', 'eramos', 'eram', 'fui',
                    'foi', 'fomos', 'foram', 'fora', 'foramos', 'seja',
                    'sejamos', 'sejam', 'fosse', 'fossemos', 'fossem',
                    'for', 'formos', 'forem', 'serei', 'sera', 'seremos',
                    'serao', 'seria', 'seriamos', 'seriam', 'tenho', 'tem',
                    'temos', 'tem', 'tinha', 'tinhamos', 'tinham', 'tive',
                    'teve', 'tivemos', 'tiveram', 'tivera', 'tiveramos',
                    'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivessemos',
                    'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei',
                    'tera', 'teremos', 'terao', 'teria', 'teriamos',
                    'teriam','pra', 'ver', 'vou', 'vendo', 'vai', 'sair', 'dar',
                    'alguem', 'fala', 'esse', 'agora', 'coisa', 'hoje', 'desse',
                    'assisti', 'quero', 'todo', 'saindo', 'quando',
                    'dizer', 'assistir', 'comprou', 'olha', 'onde', 'nenhu,'
                    'essas', 'usando', 'podemos', 'mais', 'porque', 'cinema',
                    'gente', 'ouco', 'falando', 'tava', 'meu', 'tao',
                    'nesse', 'aqui', 'fico', 'ficar', 'fazer', 'tarde', 'faz',
                    'porem', 'passando', 'ta', 'ainda', 'sei', 'acho', 'ne',
                    'pos'
                     ]

emoticons = {'vomitar': [':&', ':-&', ':=&'],
             'choro': [';(', ';-(', ';=('],
             'pensativo': [':?', ':-?', ':=?'],
             'irritado': [':@', ':-@', ':=@', 'x(', 'x-(',
                          'x=(', 'X(', 'X-(', 'X=('],
             'nerd': ['8-|', 'B-|', '8|', 'B|', '8=|', 'B=|'],
             'envergonhado': [':$', ':-$', ':=$', ':">'],
             'sou um tumulo': [':x', ':-x', ':X', ':-X',
                               ':#', ':-#', ':=x', ':=X', ':=#'],
             'piscar de olho': [';)', ';-)', ';=)'],
             'dancar': ['\\o/', '\\:D/', '\\:d/'],
             'beijo': [':*', ':=*', ':-*'],
             'porreiro': ['8=)', '8-)', 'B=)', 'B-)'],
             'sonolento': ['|-)', 'I-)', 'I=)'],
             'gargalhada': [':D', ':=D', ':-D', ':d', ':=d', ':-d'],
             'triste': [':(', ':=(', ':-('],
             'sorriso': [':)', ':=)', ':-)'],
             'surpreendido': [':o', ':=o', ':-o', ':O', ':=O', ':-O'],
             'suar': ['(:|'], 'duvida': [':^)'],
             'estupido': ['|(', '|-(', '|=('],
             'sorriso malefico': [']:)', '>:)'],
             'sem palavras': [':|', ':=|', ':-|'],
             'lingua de fora': [':P', ':=P', ':-P', ':p', ':=p', ':-p'],
             'preocupado': [':S', ':-S', ':=S', ':s', ':-s', ':=s']
             }

def sentN(x):
    if(x == 'positivo'):
        return 1
    elif(x == 'negativo'):
        return -1
    else:
        return 0

def nSent(x):
    if(x == 1):
        return 'positivo'
    elif(x == -1):
        return 'negativo'
    else:
        return 'neutro'

def trainSet(trainingSetFile):
    with open(trainingSetFile, 'r') as train_file:
        trainingSet = array(list(csv.reader(train_file, delimiter=',')))
    tweets = trainingSet[:,0]
    tweets = preprocessTweet(tweets)
    senti = array(map(sentN,trainingSet[:,1]))
    trainingSet[:, 0] = tweets
    trainingSet[:, 1] = senti
    return trainingSet

def replaceTwoOrMore(s):
    #Retirar caracter repetido

    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    r =  pattern.sub(r"\1\1",s)
    stripped = (c for c in r if  32 < ord(c) < 165)
    return ''.join(stripped)

def remover_acentos(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ascii','ignore')


def palavras_filtradas(x):
    xou = split(x)
    r = [' '.join([replaceTwoOrMore(remover_acentos(e)).lower()
                   for e in xi if (len(e) >= 3 and (e in pt_stopwords) == False)
                   ])
                   for xi in xou
         ]

    return r


def split_into_lemmas(tweet):
    bigram_vectorizer = CountVectorizer(ngram_range=(1, 3), token_pattern=r'\b\w+\b', min_df=1)
    analyze = bigram_vectorizer.build_analyzer()
    an = analyze(tweet)
    return an


def traingFeatures(tweets, stopwords):
    vectorizer = CountVectorizer(stop_words=stopwords,
                                 analyzer=split_into_lemmas,
                                 strip_accents='ascii')

    train_features = vectorizer.fit_transform([r[0] for r in tweets])
    sents =  [int(r[1]) for r in tweets]
    return train_features, sents, vectorizer

def twsenti(trainingSetFile,
                   modelFIle='./savedModel/tweetClassModel.pkl',
                   vectorizersFile='./savedModel/vectorizer.pkl'):
    savedModel = os.path.isfile(modelFIle)
    if(savedModel):
        nb = joblib.load(modelFIle)
        vectorizer = joblib.load(vectorizersFile)
    else:
        tweets = trainSet(trainingSetFile=trainingSetFile)
        train_features, sents, vectorizer = traingFeatures(tweets, pt_stopwords)
        nb = MultinomialNB()
        nb.fit(train_features, sents)
        joblib.dump(nb, modelFIle)
        joblib.dump(vectorizer, vectorizersFile)
    return nb, vectorizer.transform

def getWordCloudSent(tweets, senti, sentType):
    tws =' '.join([tweets[i] for i in range(len(senti)) if senti[i] == sentType])
    cv = CountVectorizer(min_df=0, stop_words=pt_stopwords, max_features=25)
    counts = cv.fit_transform([tws]).toarray().ravel()
    twsWords = array(cv.get_feature_names())
    twsCounts = counts / float(counts.max())
    twsDic = {twsWords[i]: str(twsCounts[i]) for i in range(len(twsWords))}
    return twsDic

def getWordFreq(tweets):
    tws = ' '.join(tweets)
    cv = CountVectorizer(min_df=0, stop_words=pt_stopwords, max_features=25)
    counts = cv.fit_transform([tws]).toarray().ravel()
    twsWords = array(cv.get_feature_names())
    twsCounts = counts / float(counts.max())
    twsDic = {twsWords[i]: str(twsCounts[i]) for i in range(len(twsWords))}
    return twsDic


def _preprocessTweet(tweet):
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', tweet)

    #Tag html
    tweet = re.sub('<[^>]+>', ' ', tweet)

    #Remove Number
    tweet = re.sub(r'(?:(?:\d+,?)+(?:\.?\d+)?)', ' ', tweet)

    tweet = re.sub('@[^\s]+', ' ', tweet)
    tweet = re.sub('[\s]+', ' ', tweet)
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    for k, v in emoticons.iteritems():
        for vi in v:
            tweet = replace(tweet, vi, k)
    return tweet


def preprocessTweet(tweet, keyWord=None):
    '''
    Funcao usada para limpar tweets contidos em um numpy array.
    '''
    tweet = lower(tweet)
    if(keyWord is not None):
        tweet = replace(tweet, keyWord, ' ')
    tweet = replace(tweet, '_', ' ')
    tweet = strip(tweet, '\'"')
    tweet = array(map(_preprocessTweet, tweet))
    return palavras_filtradas(tweet)


def _palavras_filtradas(x):
    xou = x.split(' ')
    r = [replaceTwoOrMore(remover_acentos(e)).lower()
                   for e in xou if (len(e) >= 3 and (e in pt_stopwords) == False)
                   ]

    return r

def preprocessTweet2(tweet):
    '''
    Funcao usada para limpar tweets  individuais
    '''
    tweet = tweet.lower()
    tweet = tweet.replace('_', ' ')
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', tweet)

    #Tag html
    tweet = re.sub('<[^>]+>', ' ', tweet)

    #Remove Number
    tweet = re.sub(r'(?:(?:\d+,?)+(?:\.?\d+)?)', ' ', tweet)

    tweet = re.sub('@[^\s]+', ' ', tweet)
    tweet = re.sub('[\s]+', ' ', tweet)
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    tweet = tweet.strip('\'"')


    for k, v in emoticons.iteritems():
        for vi in v:
            if(vi in tweet):
                tweet = tweet.replace(vi, k)
    return ' '.join(_palavras_filtradas(tweet))
    #return ' '.join([replaceTwoOrMore(remover_acentos(e)).lower() for e in tweet.split()])
