#!/usr/bin/env pythonico
# -*- Coding: UTF-8 -*-

__author = 'Eduardo S. Pereira'
__date = '18/05/2016'

import os
import os
import sys
path = os.path.join(request.folder,'modules')
if not path in sys.path: sys.path.append(path)

import datetime
import re
from unicodedata import normalize

import tweepy

from twsenti.twsenti import twsenti, getWordCloudSent, palavras_filtradas
from twsenti.twsenti import pt_stopwords, preprocessTweet
from numpy import array

def extrator_de_link(text):
    regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    match = re.search(regex, text)
    if match:
        return match.group()
    return False

def palavra_no_texto(palavra, texto):
    palavra = palavra.lower()
    texto = texto.lower()
    match = re.search(palavra, texto)
    if(match):
        return True
    else:
        return False

def remover_acentos(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')

def tweetClean(tweet, keyWord):
    if('entities' in tweet.keys()):

        texto = tweet['text']
        entidades = tweet[u'entities']
        hashtags = ['#' + ihash['text'] for ihash in entidades[u'hashtags']]
        urls = [iurl[u'url'] for iurl in entidades[u'urls']]
        user_mentions = ['@' + name[u'screen_name'] for name
                        in entidades[u'user_mentions']]

        if(len(user_mentions) != 0):
            for iname in user_mentions:
                texto = texto.replace(iname, '')

        if(len(urls) != 0):
            for iurls in urls:
                texto = texto.replace(iurls, '')

        if(len(hashtags) != 0):
            for itag in hashtags:
                texto = texto.replace(itag, '')
    else:
        texto = tweet['text']

    for wd in keyWord:
        lastTexto = None
        if(palavra_no_texto(wd, texto)):
            linkTw = extrator_de_link(texto)
            if(linkTw is not False):
                texto = texto.replace(linkTw, '')
                linkTw2 = extrator_de_link(texto)
                if(linkTw2 is not False):
                    texto = texto.replace(linkTw2, '')
            texto = texto.lower()
            if(not ('rt :' in texto )):
                texto = texto.replace(' https:...', '')
                texto = texto.replace('http...', '')
                texto = texto.replace('https...', '')
                texto = texto.replace('https:...', '')
                texto = texto.replace('http:...', '')
                texto = texto.replace('...', '')
                texto = remover_acentos(texto.encode('utf-8'))
                texto = texto.replace('\n', '')
                texto = texto.lower()
                texto = texto.translate(None, '":,!?#$@%*&')
                texto = texto.replace(wd, '')
                lastTexto = texto

    if(lastTexto is not None):
        return lastTexto
    else:
        return False

def tweetSearch(keyWord, lat, lng, raio, auth):

    TRAINING_FILE = os.path.join(request.folder,
                                 'private/trainingSet/filmes.csv')
    MODELFILE = os.path.join(request.folder,
                             'private/trainingSet/tweetClassModel.pkl')
    VECTORIZERFILE = os.path.join(request.folder,
                                  'private/trainingSet/vectorizer.plk')
    sentimento, vectorize = twsenti(trainingSetFile=TRAINING_FILE,
                            modelFIle=MODELFILE,
                            vectorizersFile=VECTORIZERFILE)

    api = tweepy.API(auth)
    search_tweets = api.search(q=keyWord,
                               lang='pt',
                               locale='br',
                               geocode='%s,%s,%skm' %(lat, lng, raio),
                               count=100)


    tweets = []
    tweetsId = []
    print(len(search_tweets))
    for tweet in search_tweets:

        tw = False
        if(palavra_no_texto(keyWord, tweet.text)):
            tw = tweet.text.encode('utf-8')
            tw = tw.replace(keyWord, '')
        if((tw in tweets) is False and tw is not False):
            tweets.append(tw)
            tweetsId.append(tweet.id)

    tweets = preprocessTweet(array(tweets))
    sent = sentimento.predict(vectorize(tweets))

    return sent, [getWordCloudSent(tweets, sent, 1),
                  getWordCloudSent(tweets, sent, -1)], tweetsId


def tweetSent(tweet):
    arquivo = 'private/trainingSet/filmes.csv'
    TRAINING_FILE = os.path.join(request.folder, arquivo)
