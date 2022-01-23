# -*- coding: utf-8 -*-
import os, urllib.parse
from bottle import run, route, request
from bottle import request
from bottle import HTTPResponse
import inspect

from config import *

import urllib.request
import logging
from requests_oauthlib import OAuth1Session
from oauthlib.oauth1 import Client
import json

def location(depth=0):
    frame = inspect.currentframe().f_back
    return (frame.f_code.co_filename, frame.f_lineno)

@route("/")
def hello_world():
    print("*** hello_world() START ***")
    print("*** hello_world() END ***")
    response = setResponse(200, "*** hello_world() END ***")
    return response

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'
 
# フォーマットを指定 (https://docs.python.jp/3/library/logging.html#logrecord-attributes)
_detail_formatting = '%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s'

"""
Twitterポストします
"""
@route('/twi', method='POST')
def twitter_post(data=None):
    print("*** twitter_post() START ***")

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
            print("msg: ", msg)

            activeAccount = oauthByTeamId(teamId)

            # Tw API verをチェックし処理分岐
            # apiVer2 = twApiVer2(teamId)
            # print( inspect.getmembers( activeAccount) , location())
            # if apiVer2:
            print("一律ver2")
            url = "https://api.twitter.com/2/tweets"
            json_data = {"text" : msg}
            req = activeAccount.post(url, data = json.dumps(json_data))
            print(json_data, location())
            # else:
            #     print("ver1")
            #     url = "https://api.twitter.com/1.1/statuses/update.json?status=" + msg
            #     req = activeAccount.post(url)

            # レスポンスを確認
            if req.status_code != (200 or 201 or 403):
                print (vars(req), location())
            response = setResponse(req.status_code, "*** twitter_post() ERROR ***")
            return response
        else:
            print("teamIdが見つからなかったのでTwitterポストしませんでした ", location(), " ", request.args)
    except Exception as e:
        print(sys.exc_info(), location())
    print("*** twitter_post() END ***")
    response = setResponse(req.status_code, "*** twitter_post() END ***")
    return response

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(twitterIdToFav)のツイートをファボします
ファボするユーザーは引数2(teamId)
routeは用意してるが実質呼ばれることはなく、1つ下の'twitter_search'からinternalで呼ばれる
'''
@route('/twFav?id=:twitterIdToFav&teamId=:teamId', method='GET')
def twitter_fav(twitterIdToFav, teamId):
    print("*** twitter_fav() START ***")

    # Tw API verをチェックし処理分岐
    apiVer2 = twApiVer2(teamId)
    if apiVer2:
        # ユーザーIDがわからないとfavできなくなった。対処法を考えないと
        return 555
    else:
        url = "https://api.twitter.com/1.1/favorites/create.json?id=" + twitterIdToFav
    
    activeAccount = oauthByTeamId(teamId)
    req = activeAccount.post(url)

    # レスポンスを確認
    if req.status_code != (200 or 201 or 403):
        print ("Error: %d" % req.status_code, location(), req)
    print("*** twitter_fav() END ***")
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
    print("*** twitter_search() START ***")
    word = request.query.get('q')
    teamId = request.query.get('teamId')
    count = 0

    # Tw API verをチェックし処理分岐
    apiVer2 = twApiVer2(teamId)
    if apiVer2:
        response = setResponse(200, "*** twitter_search() v2未開通 ***")
        return response
    else:
        url = "https://api.twitter.com/1.1/search/tweets.json?q=" + word

    activeAccount = oauthByTeamId(teamId)
    req = activeAccount.get(url)

    # レスポンスを確認
    if req.status_code == 200 or 201:
        resJson = json.loads(req._content.decode('utf-8'))
        
        for item in resJson["statuses"]:
            status = twitter_fav(item["id_str"], teamId)
            if status == 200:
                print(item["id_str"] + " Success teamId=" + teamId, " count:", count)
                count = count + 1
            elif status == (429 or 403):
                print("Error: " + status + ". Break transaction.")
                response = setResponse(200, "*** twitter_search() END ***")
                return response
            if count >= 30:
                break
    else:
        print ("Error: %d" % req.status_code, location(), " ", str(req))
    
    print("*** twitter_search() END ***")
    response = setResponse(req.status_code, "*** twitter_search() END ***")
    return response

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(userToFollow)のユーザーをフォロバします
実行ユーザーは引数2(teamId)
routeはあるが実質'twitter_folB'からinternalで呼ばれます
'''
@route('/twFol?id=:userToFollow&teamId=:teamId', method='GET')
def twitter_follow(userToFollow, teamId):
    print("*** twitter_follow() START ***")

    activeAccount = oauthByTeamId(teamId)

    # Tw API verをチェックし処理分岐
    apiVer2 = twApiVer2(teamId)
    if apiVer2:
        accountId= twitterIdByTeamId(teamId)
        url = "https://api.twitter.com/2/users/" + accountId + "/following"
        json_data = {"target_user_id" : userToFollow}
        req = activeAccount.post(url, data = json.dumps(json_data))
    else:
        url = "https://api.twitter.com/1.1/friendships/create.json?user_id=" + str(userToFollow)
        req = activeAccount.post(url)
    
    resCode = None

    # レスポンスを確認
    if req.status_code == 200 or 201:
        print ("フォロバ成功: ", userToFollow)
        resCode = req.status_code
    elif req.status_code == 403:
        res = json.loads(req._content.decode('utf-8'))
        errCode = res["errors"][0]["code"]
        if errCode == 160:
            print("フォロリクsent: ", userToFollow)
            resCode = 200
    else:
        print ("フォロバError: %d" % req.status_code, userToFollow, location())
        try:
            print(vars(req))
        except Exception as e:
            print(e.args)
        resCode = req.status_code
    print("*** twitter_follow() END ***")
    return resCode

'''
https://qiita.com/yubais/items/dd143fe608ccad8e9f85
引数1(teamId)のアカで、(フォローしてされてるユーザー)-(フォローしてるユーザー)をして
フォロバしていないユーザーはフォロバします
Javaから呼んでます
'''
@route('/twFolB', method='GET')
def twitter_folB():
    print("*** twitter_folB() START ***")

    teamId = request.query.get('teamId')

    # Tw API verをチェックし処理分岐
    apiVer2 = twApiVer2(teamId)
    if apiVer2:
        accountId= twitterIdByTeamId(teamId)
        url_followers = "https://api.twitter.com/2/users/" + accountId + "/followers?user.fields=id"
        url_follows = "https://api.twitter.com/2/users/" + accountId + "/following?user.fields=id"
    else:
        url_followers = "https://api.twitter.com/1.1/followers/ids.json"
        url_follows = "https://api.twitter.com/1.1/friends/ids.json"

    activeAccount = oauthByTeamId(teamId)

    # フォローしてる人を確認します
    req2 = activeAccount.get(url_follows)

    # レスポンスを確認
    if req2.status_code == 200 or 201:
        followingRes = json.loads(req2._content.decode('utf-8'))
    else:
        print ("フォローしてる人 get error: %d" % req2.status_code, location())


    # フォロワーを検索します
    req = activeAccount.get(url_followers)
    # レスポンスを確認
    if req.status_code == 200 or 201:
        followerRes = json.loads(req._content.decode('utf-8'))
    else:
        print ("フォロワー get error: %d" % req.status_code, location())

    # フォローしてる人の中に入っていないフォロワーは今回Jobでのフォロー対象
    followTargetArr = []
    if apiVer2:
        followingUserId = []
        for userId in followingRes["data"]:
            followingUserId.append(userId["id"])

        followerUserId = []
        for userId in followerRes["data"]:
            followerUserId.append(userId["id"])

        for twiId in followerUserId:
            if twiId not in followingUserId:
                followTargetArr.append(twiId)
    else:
        for twiId in followerRes['ids']:
            if twiId not in followingRes['ids']:
                followTargetArr.append(twiId)
    
    if len(followTargetArr) > 0:
        for targetId in followTargetArr:
            status = twitter_follow(targetId, teamId)
    print("*** twitter_folB() END ***")
    response = setResponse(req.status_code, "*** twitter_folB() END ***")
    return response

"""
teamIdを渡せばOAuthオブジェクトを返却します
ジャニ以外のTwitterアカも対応
"""
def oauthByTeamId(teamId=0):
    print("*** oauthByTeamId() START ***")

    if type(teamId) == str:
        teamId = int(teamId)

    # OAuth認証で POST method で投稿(チームごと異なる分岐)
    activeAccount = None
    try:
        if teamId == 17: # SixTONES
            print(17)
            activeAccount = OAuth1Session(sixtones_consumer_key, sixtones_consumer_secret, sixtones_token, sixtones_token_secret, client_class=CustomClient)
        elif teamId == 6: # Snowman
            print(6)
            activeAccount = OAuth1Session(snowman_consumer_key, snowman_consumer_secret, snowman_token, snowman_token_secret, client_class=CustomClient)
        elif teamId == 16: # King & Prince
            print(16)
            activeAccount = OAuth1Session(kinpri_consumer_key, kinpri_consumer_secret, kinpri_token, kinpri_token_secret, client_class=CustomClient)
        elif teamId == 18: # なにわ男子
            print(18)
            activeAccount = OAuth1Session(naniwa_consumer_key, naniwa_consumer_secret, naniwa_token, naniwa_token_secret, client_class=CustomClient)
        elif teamId == 8: # Sexy Zone
            print(8)
            activeAccount = OAuth1Session(sexyzone_consumer_key, sexyzone_consumer_secret, sexyzone_token, sexyzone_token_secret, client_class=CustomClient)
        elif teamId == 100: # @LjtYdg
            print(100)
            activeAccount = OAuth1Session(love_consumer_key, love_consumer_secret, love_token, love_token_secret, client_class=CustomClient)
        elif teamId == 101: # @ChiccaSalak
            print(101)
            activeAccount = OAuth1Session(tosi_consumer_key, tosi_consumer_secret, tosi_token, tosi_token_secret, client_class=CustomClient)
        elif teamId == 102: # @BlogChicca
            print(102)
            activeAccount = OAuth1Session(engineer_consumer_key, engineer_consumer_secret, engineer_token, engineer_token_secret, client_class=CustomClient)
        elif teamId == 103: # @Berry_chicca
            print(103)
            activeAccount = OAuth1Session(berry_consumer_key, berry_consumer_secret, berry_token, berry_token_secret, client_class=CustomClient)
        else: # General Account
            print("General")
            activeAccount = OAuth1Session(consumer_key, consumer_secret, token, token_secret, client_class=CustomClient)
    except Exception:
        print ("Error on finding Twitter account", location())
    print("*** oauthByTeamId() END ***")
    return activeAccount

"""
引数のteamidはtwitter apiがv2対応かどうかを判断します
（全部v2にしたほうがいいんじゃない？）
ひとまず、v2でしかポストできないアカはv2になります
"""
def twApiVer2(teamId):
    print("*** twApiVer2() START ***")

    if type(teamId) == str:
        teamId = int(teamId)

    result = False
    try:
        if teamId == 100: # @LjtYdg
            result = True
        elif teamId == 101: # @ChiccaSalak
            result = True
        elif teamId == 102: # @BlogChicca
            result = True
        elif teamId == 103: # @Berry_chicca
            result = True
        else: # General Account
            result = False
    except Exception:
        print ("Error on finding Twitter account", location())
    print("*** twApiVer2() END ***")
    return result

"""
引数teamIdを元に、twitterアカのIDを返却します
V2 APIで使用します
"""
def twitterIdByTeamId(teamId):
    print("*** twitterIdByTeamId() START ***")

    if type(teamId) == str:
        teamId = int(teamId)

    result = None
    try:
        if teamId == 17: # SixTONES
            result = "1411427767443283969"
        elif teamId == 6: # Snowman
            result = "1409169347277332481"
        elif teamId == 16: # King & Prince
            result = "1411429221038116866"
        elif teamId == 18: # なにわ男子
            result = "1418288638345965568"
        elif teamId == 8: # Sexy Zone
            result = "1418289988827901953"
        elif teamId == 100: # @LjtYdg
            result = "1478868616657645570"
        elif teamId == 101: # @ChiccaSalak
            result = "1329526833461661696"
        elif teamId == 102: # @BlogChicca
            result = "1353959290596331523"
        elif teamId == 103: # @Berry_chicca
            result = "1267562271036674049"
        else: # General Account
            result = "1409384870745313286"
    except Exception:
        print ("Error on finding Twitter account", location())
    print("*** twitterIdByTeamId() END ***")
    return result

"""
httpResponseを作成します
"""
def setResponse(status=200, message=''):
    body = json.dumps({'status': status, 'message': message})
    response = HTTPResponse(status = status, body = body)
    response.set_header('Content-Type', 'application/json')
    return response

class CustomClient(Client):
    def _render(self, request, formencode=False, realm=None):
        print("*** CustomClient._render() START ***")
        request.headers['Content-type'] = "application/json"
        print("*** CustomClient._render() END ***")
        return super()._render(request, formencode, realm)

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
