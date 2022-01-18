# -*- coding: utf-8 -*-
from ast import Str
import os, twitter, urllib.parse
from bottle import run, route, request, HTTPResponse
from bottle import get, post, request
import inspect

from config import *

import urllib.request
import logging
from requests_oauthlib import OAuth1Session
import json

def location(depth=0):
    frame = inspect.currentframe().f_back
    return (frame.f_code.co_filename, frame.f_lineno)

@route("/")
def hello_world():
    return 'Hello', 200

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'
 
# フォーマットを指定 (https://docs.python.jp/3/library/logging.html#logrecord-attributes)
_detail_formatting = '%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s'

@route('/twi', method='POST')
def twitter_post(data=None):

    teamId = request.query.get('teamId')

    proceedFlg = True

    try:
        if teamId == None:
            print("teamIdが見つかりませんでした ", location(), " ", request)
            proceedFlg = False

        if request != None and request.json != None and request.json['title'] != None:
            msg = urllib.parse.unquote(request.json['title'], encoding='shift-jis')
        elif data != None and data.get('title') != None:
            msg = urllib.parse.unquote(data.get('title'), encoding='shift-jis')
        else:
            print("msgが見つかりません ", location())
            proceedFlg = False

        if proceedFlg:
            url = "https://api.twitter.com/1.1/statuses/update.json?status=" + msg;

            activeAccount = oauthByTeamId(teamId)
            req = activeAccount.post(url)

            # レスポンスを確認
            if req.status_code != (200 or 403):
                print ("Error: %d" % req.status_code, location(), " ")
                print ("vars(req) ", vars(req))
                print ("str(req) ", str(req))
                print ("sys.exc_info()", sys.exc_info())
            return req.status_code
        else:
            print("teamIdが見つからなかったのでTwitterポストしませんでした ", location(), " ", request.args)
    except Exception as e:
        print(sys.exc_info(), location())
    return None

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(twitterIdToFav)のツイートをファボします
ファボするユーザーは引数2(teamId)
routeは用意してるが実質呼ばれることはなく、1つ下の'twitter_search'からinternalで呼ばれる
'''
@route('/twFav?id=:twitterIdToFav&teamId=:teamId', method='GET')
def twitter_fav(twitterIdToFav, teamId):

    url = "https://api.twitter.com/1.1/favorites/create.json?id=" + twitterIdToFav;

    activeAccount = oauthByTeamId(teamId)
    req = activeAccount.post(url)

    # レスポンスを確認
    if req.status_code != (200 or 403):
        print ("Error: %d" % req.status_code, location(), req)
    return req.status_code

"""
検索ワードからツイートを検索します
→ファボに使う
[DEF]30件ファボしたら終わる
Javaから呼んでます
https://qiita.com/masaibar/items/e3b6911aee6741037549#%E5%8F%97%E3%81%91%E5%8F%96%E3%81%A3%E3%81%9F%E3%83%91%E3%83%A9%E3%83%A1%E3%83%BC%E3%82%BF%E3%82%92%E5%88%A9%E7%94%A8%E3%81%99%E3%82%8B
"""
@route('/twSearch', method='GET')
def twitter_search():
    word = request.query.get('q')
    teamId = request.query.get('teamId')
    print(teamId)
    count = 0
    url = "https://api.twitter.com/1.1/search/tweets.json?q=" + word

    activeAccount = oauthByTeamId(teamId)
    req = activeAccount.get(url)

    # レスポンスを確認
    if req.status_code == 200:
        resJson = json.loads(req._content.decode('utf-8'))
        
        for item in resJson["statuses"]:
            status = twitter_fav(item["id_str"], teamId)
            if status == 200:
                print(item["id_str"] + " Success teamId=" + teamId, " count:", count)
                count = count + 1
            elif status == (429 or 403):
                print("Error: " + status + ". Break transaction.")
                return
            if count >= 30:
                break
    else:
        print ("Error: %d" % req.status_code, location(), " ", str(req))
    
    return 200

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(userToFollow)のユーザーをフォロバします
実行ユーザーは引数2(teamId)
routeはあるが実質'twitter_folB'からinternalで呼ばれます
'''
@route('/twFol?id=:userToFollow&teamId=:teamId', method='GET')
def twitter_follow(userToFollow, teamId):

    url = "https://api.twitter.com/1.1/friendships/create.json?user_id=" + str(userToFollow);

    activeAccount = oauthByTeamId(teamId)
    req = activeAccount.post(url)
    resCode = None

    # レスポンスを確認
    if req.status_code == 200:
        print ("OK: ", userToFollow)
        resCode = req.status_code
    elif req.status_code == 403:
        res = json.loads(req._content.decode('utf-8'))
        errCode = res["errors"][0]["code"]
        if errCode == 160:
            print("Request sent", userToFollow)
            resCode = 200
    else:
        print ("Error: %d" % req.status_code, userToFollow, location())
        resCode = req.status_code
    return resCode

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(teamId)のアカで、(フォローしてされてるユーザー)-(フォローしてるユーザー)をして
フォロバしていないユーザーはフォロバします
Javaから呼んでます
'''
@route('/twFolB', method='GET')
def twitter_folB():

    teamId = request.query.get('teamId')

    url_followers = "https://api.twitter.com/1.1/followers/ids.json"
    url_follows = "https://api.twitter.com/1.1/friends/ids.json"

    activeAccount = oauthByTeamId(teamId)

    # フォローしてる人を確認します
    req2 = activeAccount.get(url_follows)

    # レスポンスを確認
    if req2.status_code == 200:
        print("***********************")
        followingRes = json.loads(req2._content.decode('utf-8'))
        # これがフォローしてる人のリスト
        print(followingRes['ids'])
    else:
        print ("Error: %d" % req2.status_code, location())


    # フォロワーを検索します
    req = activeAccount.get(url_followers)
    # レスポンスを確認
    if req.status_code == 200:
        followerRes = json.loads(req._content.decode('utf-8'))
        # これがフォロワーのリスト
        print(followerRes['ids'])
    else:
        print ("Error: %d" % req.status_code, location())

    # フォローしてる人の中に入っていないフォロワーは今回Jobでのフォロー対象
    followTargetArr = []
    for twiId in followerRes['ids']:
        if twiId not in followingRes['ids']:
            followTargetArr.append(twiId)
    
    if len(followTargetArr) > 0:
        for targetId in followTargetArr:
            status = twitter_follow(targetId, teamId)
    return 200

"""
teamIdを渡せばOAuthオブジェクトを返却します
ジャニ以外のTwitterアカも対応
"""
def oauthByTeamId(teamId=0):
    print("oauthByTeamId")

    if type(teamId) == str:
        teamId = int(teamId)

    # OAuth認証で POST method で投稿(チームごと異なる分岐)
    activeAccount = None
    try:
        if teamId == 17: # SixTONES
            print(17)
            activeAccount = OAuth1Session(sixtones_consumer_key, sixtones_consumer_secret, sixtones_token, sixtones_token_secret)
        elif teamId == 6: # Snowman
            print(6)
            activeAccount = OAuth1Session(snowman_consumer_key, snowman_consumer_secret, snowman_token, snowman_token_secret)
        elif teamId == 16: # King & Prince
            print(16)
            activeAccount = OAuth1Session(kinpri_token, kinpri_token_secret, kinpri_consumer_key, kinpri_consumer_secret)
        elif teamId == 18: # なにわ男子
            print(18)
            activeAccount = OAuth1Session(naniwa_consumer_key, naniwa_consumer_secret, naniwa_token, naniwa_token_secret)
        elif teamId == 8: # Sexy Zone
            print(8)
            activeAccount = OAuth1Session(sexyzone_consumer_key, sexyzone_consumer_secret, sexyzone_token, sexyzone_token_secret)
        elif teamId == 100: # @LjtYdg
            print(100)
            activeAccount = OAuth1Session(love_consumer_key, love_consumer_secret, love_token, love_token_secret)
        elif teamId == 101: # @ChiccaSalak
            print(101)
            activeAccount = OAuth1Session(tosi_consumer_key, tosi_consumer_secret, tosi_token, tosi_token_secret)
        elif teamId == 102: # @BlogChicca
            print(102)
            activeAccount = OAuth1Session(engineer_consumer_key, engineer_consumer_secret, engineer_token, engineer_token_secret)
        elif teamId == 103: # @Berry_chicca
            print(103)
            activeAccount = OAuth1Session(berry_consumer_key, berry_consumer_secret, berry_token, berry_token_secret)
        else: # General Account
            print("General")
            activeAccount = OAuth1Session(consumer_key, consumer_secret, token, token_secret)
    except Exception:
        print ("Error on finding Twitter account", location())
    return activeAccount

"""
LOG_LEVEL_FILEレベル以上のログをファイルに出力する設定
"""
# datetime_moduleモジュールを呼び出す側(test.py)で出力形式などの基本設定をする
logging.basicConfig(
    # LOG_LEVEL_FILE = 'DEBUG' なら logging.DEBUGを指定していることになる
    level=getattr(logging, LOG_LEVEL_FILE),
    format=_detail_formatting,
    filename='./logs/yahoo.log'
)

console = logging.StreamHandler()
# LOG_LEVEL_CONSOLE = 'INFO' なら logging.INFOを指定していることになる
console.setLevel(getattr(logging, LOG_LEVEL_CONSOLE))
console_formatter = logging.Formatter(_detail_formatting)
console.setFormatter(console_formatter)

@route("/env")
def yahoo():
    return ENV

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
