# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

ROOT = 'http://'+request.env.http_host+'/'

CONSUMER_KEY = 'QucxudfPspFsSQe0hYquFUZXJ'
CONSUMER_SECRET = 'NY0cA3UjJORBefqhV6MUaUY3T78L8f2uFEqB8Jzzd62WkasmEe'
CALLBACK = ROOT + request.application + '/default/callback'

FB_CLIENT_ID='1194410603933695'#'1632054960443151'
FB_CLIENT_SECRET='d5f30f76947acad0f5b78078b85a0762'#"be120d94c0a8ee65f3a549751c002672"
CALLBACKFACEBOOK = ROOT + request.application + '/default/callbackface'

import tweepy
from facebook import get_user_from_cookie, GraphAPI
import urllib2
from twsenti.twsenti import palavras_filtradas, twsenti, getWordCloudSent
from numpy import array
import datetime

TESTEMODE = False

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict()


def callback():
    request_token = session.request_token
    session.request_token = None
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
    auth.request_token = request_token
    verifier = request.vars['oauth_verifier']
    auth.get_access_token(verifier)
    session.token = (auth.access_token, auth.access_token_secret)
    redirect(URL('default', 'request_twitter'))

def request_twitter():

    if(session.token is not None):
        token, token_secret = session.token
        authTW = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)

        authTW.set_access_token(token, token_secret)
        api = tweepy.API(authTW)
        session.userInfo = api.me()

        redirect(URL("default", 'search'))

    else:
        redirect(URL("default", 'twitter'))

def twitter():
    if(session.token is None):
        auth =  tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        url = auth.get_authorization_url(signin_with_twitter=True)
        session.request_token = auth.request_token
        redirect(url)
    else:
        token, token_secret = session.token
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        try:
            auth.set_access_token(token, token_secret)
        except:
            session.token = None
            auth =  tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
            url = auth.get_authorization_url()
            session.request_token = auth.request_token
            redirect(url)

        redirect(URL("default", 'search'))

def facebookAuth():
    url = 'https://www.facebook.com/dialog/oauth?'
    url += 'client_id=%s&client_secret=%s&redirect_uri=%s&scope=email,public_profile' % (FB_CLIENT_ID,
                                                              FB_CLIENT_SECRET,
                                                              CALLBACKFACEBOOK)
    redirect(url)

def callbackface():
    if('code' in request.vars.keys()):
        code = request.vars['code']
        url = 'https://graph.facebook.com/v2.3/oauth/access_token?'
        url += 'client_id=%s&client_secret=%s&redirect_uri=%s&code=%s' % (
                                                             FB_CLIENT_ID,
                                                              FB_CLIENT_SECRET,
                                                              CALLBACKFACEBOOK,
                                                              code)
        response = urllib2.urlopen(url)
        session.facebookToken = json.loads(response.read())
        redirect(URL('default', 'fanpage'))

@auth.requires_login()
def fanpage():
    ## Define oauth application id and secret.
    if(session.facebookToken is None):
        redirect(URL('default', 'facebookAuth'))
    print("TokenFace")
    print(session.facebookToken['access_token'])
    graph = GraphAPI(session.facebookToken['access_token'])
    #strr = "olhardigital/feed?fields=comments,message"
    #profile = graph.get_object(strr)

    form = SQLFORM.factory(Field('search',requires=IS_NOT_EMPTY()),
                           submit_button='Search')
    form.element(_name='search')['_type'] = 'search'
    pagesFeed = []
    fields = 'picture,engagement,description,name,about,link,cover,category'
    pages = []

    if form.accepts(request):
            pages = graph.request('search', {'q': form.vars.search,
                                         'type': 'page',
                                         'limit': 5,
                                         'fields': fields}
                              )['data']
            if pages == []:
                session.flash = 'Não existem resultados para esta pesquisa.'
                redirect(URL('fanpage'))

    return dict(pages=pages, form=form)


@auth.requires_login()
def loadingSentiFanpage():
    pageId = request.args[0]

    return dict(pageId=pageId)

@auth.requires_login()
def sentifanpage():
    pageId = request.args[0]


    if(session.facebookToken is None):
        redirect(URL('default', 'facebookAuth'))

    TRAINING_FILE = os.path.join(request.folder,
                                 'private/trainingSet/filmes.csv')
    MODELFILE = os.path.join(request.folder,
                             'private/trainingSet/tweetClassModel.pkl')
    VECTORIZERFILE = os.path.join(request.folder,
                                  'private/trainingSet/vectorizer.plk')
    sentimento, vectorize = twsenti(trainingSetFile=TRAINING_FILE,
                            modelFIle=MODELFILE,
                            vectorizersFile=VECTORIZERFILE)

    graph = GraphAPI(session.facebookToken['access_token'])



    posts = None
    labels = None
    dataP = None
    dataN = None

    if(TESTEMODE is False):
        session.posts = None
        session.labels = None
        session.dataP = None
        session.dataN = None


    if(session.posts is None):
        strr = "%s/feed?fields=comments,message,picture" % pageId
        feed = graph.get_object(strr)['data']

        posts = []
        labels = []
        dataP = []
        dataN = []
        for fi in feed:
            if ('comments' in fi.keys()):
                picture = None
                if('picture' in fi.keys()):
                    picture = fi['picture']
                comments = palavras_filtradas(array([ci['message'].encode('utf-8')
                                                for ci in fi['comments']['data']
                                                if 'message' in ci.keys()]))
                nameUserComments = array([
                remover_acentos(ci['from']['name'].split(' ')[0].encode('utf-8'))
                                                for ci in fi['comments']['data']])
                message = None
                if('message' in fi.keys()):
                    message = fi['message']

                sent = sentimento.predict(vectorize(comments))
                total = [len([i for i in sent if i == 1]),
                         len([i for i in sent if i == -1])]
                postInfo = graph.get_object(fi['id'])
                labels.append(postInfo['created_time'].split('T')[0])
                dataP.append(total[0])
                dataN.append(total[1])
                dataPostagem = postInfo['created_time'].split('T')[0]
                dataPostagem = dataPostagem.split('-')
                dataPostagem = '%s-%s-%s' %(dataPostagem[2],
                                            dataPostagem[1],
                                            dataPostagem[0])
                posts.append({'message': message,
                              'id': postInfo['id'],
                              'picture':picture,
                              'data': dataPostagem,
                              'positivos': total[0],
                              'negativos': total[1]
                              })
                if(TESTEMODE is True):
                    session.posts = posts
                    session.labels = labels
                    session.dataP = dataP
                    session.dataN = dataN
    else:
        posts = session.posts
        labels = session.labels
        dataP = session.dataP
        dataN = session.dataN


    return dict(posts=posts, labels=labels, dataP=dataP, dataN=dataN)

'''



    mesg = []

    for d in profile['data']:

        if ('comments' in d.keys()):
            comments = palavras_filtradas(array([di['message'].encode('utf-8')
                                            for di in d[u'comments']['data']]))
            sent = sentimento.predict(vectorize(comments))
            total = [len([i for i in sent if i == 1]),
                     len([i for i in sent if i == -1])]
            pWC = None
            try:
                pWC = getWordCloudSent(comments, sent, 1)
            except:
                pass


            #nWC = getWordCloudSent(comments, sent, -1)
            if('message' in d.keys()):
                mesg.append([d['id'], d['message'], total, pWC])
            else:
                mesg.append([d['id'], total, pWC])
'''



@auth.requires_login()
def search():
    token, token_secret = session.token
    authTw = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
    try:
        authTw.set_access_token(token, token_secret)
    except:
        session.token = None
        redirect(URL("default", 'twitter'))

    db.last_section.insert(user_id=auth.user_id,
                           lastSection=datetime.datetime.now())
    db.commit()

    image = session.userInfo.profile_image_url
    userName = session.userInfo.name

    form = SQLFORM.factory(Field('search',requires=IS_NOT_EMPTY()),
                           Field('lat', requires=IS_NOT_EMPTY()),
                           Field('lng', requires=IS_NOT_EMPTY()),
                           Field('raio', requires=IS_NOT_EMPTY()),
                           Field('zoom'),
                           submit_button='Search')
    form.element(_name='search')['_type'] = 'search'
    form.element(_name='lat')['_id'] = 'lat'
    form.element(_name='lng')['_id'] = 'lng'
    form.element(_name='raio')['_id'] = 'raio'
    form.element(_name='zoom')['_id'] = 'zoom'
    form.element(_name='zoom')['_type'] = 'hidden'
    form.element(_name='lat')['_type'] = 'hidden'#Esconde campo do formulário
    form.element(_name='lng')['_type'] = 'hidden'
    form.element(_name='raio')['_type'] = 'hidden'
    latlon = [-23.1774695, -45.8789595]
    raio = 50
    zoom = 13
    total = [0,0]
    forWordCloud= None
    posTW = []
    negTW = []
    if form.accepts(request, hideerror=True):
        search = form.vars.search
        lat = float(form.vars.lat)
        lng = float(form.vars.lng)
        latlon = [lat, lng]
        raio = int(float(form.vars.raio))
        zoom = int(float(form.vars.zoom))
        try:
            result = tweetSearch(search, lat, lng, raio, authTw)
        except:
            session.flash = 'Não existem resultados para esta pesquisa.'
            redirect(URL('search'))
        total = [len([i for i in result[0] if i == 1]),
                 len([i for i in result[0] if i == -1])]

        kP = 0
        kN = 0
        for i in range(len(result[0])):
            if(result[0][i] == 1):
                if(kP < 5):
                    posTW.append(result[2][i])
                    kP +=1
            else:
                if(kN < 5):
                    negTW.append(result[2][i])
                    kN += 1

        forWordCloud = [result[1][0], result[1][1]]
        response.flash = 'Pesquisa concluida com sucesso.'
    elif form.errors:
        print(form.errors)
        response.flash = "Escolha a localização, e em seguida clique no mapa para determinar a área de interesse!"

    return dict(form=form,
                latlon=latlon,
                raio=raio,
                total=total,
                zoom=zoom,
                forWordCloud=forWordCloud,
                imageUser=image,
                userName=userName,
                posTW=posTW,
                negTW=negTW
                )


@auth.requires_login()
def base_usuarios():
    from gluon.serializers import json
    from numpy import array, unique
    users = db().select(db.auth_user.ALL, orderby=db.auth_user.created_on)
    userPerDay = unique(array([[s['created_on'].date()]  for s in users]),
                        return_counts=True)
    sectionByUserPerDay = []
    for u in users:
        print unique(array([s['lastSection'].date() for s in
         u.last_section.select(db.last_section.lastSection)]),
                     return_counts=True)

    return dict(userPerDay=userPerDay)


def map():
    return dict()

def politicas():
    '''Página de políticas de privacidade'''
    return dict()

def termos():
    '''Página dos termos de uso'''
    return dict()

def faq():
    '''Página da faq'''
    return dict()

def sobre():
    '''Página sobre'''
    return dict()

def user():


    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    if(session.userInfo is None):
        redirect(URL('default', 'twitter'))
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
