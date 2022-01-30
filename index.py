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

"""
https://qiita.com/ymko/items/b46d32b98f013f06d805
"""
def location(depth=0):
    frame = inspect.currentframe().f_back
    return (frame.f_code.co_filename, frame.f_lineno)

"""
tupleをstrに変換して返します
location()を文字列にしたい時に使う想定
"""
def tuple_str(location):
    return ','.join(map(str,location))

"""
HttpRequestを引数に渡すと、responseのcontent内部をJsonに変換して返します
Twitter APIのresponse中身を取り出すために使用。汎用。
Errorの場合はここでエラーを表示し、Noneを返却
"""
def content_by_req(req):
    inner = json.loads(req._content.decode('utf-8'))

    if "errors" in inner.keys():
        print(vars(req))
        inner = None
    return inner

@route("/")
def hello_world():
    print("*** hello_world() START ***")
    print("*** hello_world() END ***")
    response = setResponse(200, "*** hello_world() END ***")
    return response

@route("/tmp")
def rmp():
    response = tweet_v2(17, "")
    return response

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'
 
# フォーマットを指定 (https://docs.python.jp/3/library/logging.html#logrecord-attributes)
_detail_formatting = '%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s'

### PUREなAPI送信のためのメソッドを共通化で作ります。各メソッドから呼び出す想定 ###
## 引数エラーチェックなしのため呼び出す側で問題ない時だけ呼び出して
## returns response
"""
Post tweet v1.1
"""
# もう使わないのでnot implemented

"""
Post tweet API v2
"""
def tweet_v2(teamId=0, msg=""):
    print("*** tweet_v2() START ***")
    print("teamId: ", teamId, " msg:", msg)

    activeAccount = oauthByTeamId(teamId)
    url = "https://api.twitter.com/2/tweets"
    json_data = {"text" : msg}

    resMsg = ""

    try:
        req = activeAccount.post(url, data = json.dumps(json_data))

        # 汎用メソッドでレスポンスからデータを取り出す
        resData = content_by_req(req)
        if resData:
            resMsg = "Success: " + tuple_str(location())
        else:
            resMsg = "Error: " + tuple_str(location())
    except Exception as e:
        print(sys.exc_info(), e, location())
    print("*** tweet_v2() END ***")
    response = setResponse(req.status_code, resMsg)
    return response

"""
Like a tweet v2
"""
def like_v2(teamId=0, tweetId=""):
    print("*** like_v2() START ***")
    print("teamId: ", teamId, " tweetId:", tweetId)
    
    activeAccount = oauthByTeamId(teamId)
    accountId = twitterIdByTeamId(teamId)
    resMsg = ""

    url = "https://api.twitter.com/2/users/" + accountId + "/likes"
    data = {"tweet_id": tweetId}
    try:
        req = activeAccount.post(url, data = json.dumps(data))

        # 汎用メソッドでレスポンスからデータを取り出す
        resData = content_by_req(req)
        if resData:
            resMsg = "Success: " + tuple_str(location())
        else:
            resMsg = "Error: " + tuple_str(location())
    except Exception as e:
        print(sys.exc_info(), e, location())
    print("*** like_v2() END ***")
    response = setResponse(req.status_code, resMsg)
    return response

"""
Twitterポストします
"""
@route('/twi', method='POST')
def twitter_post(data=None):
    print("*** twitter_post() START ***")

    teamId = request.query.get('teamId')
    resMsg = ""

    if teamId == None:
        print("teamIdが見つかりませんでした ", location(), " ", request)
        resMsg = "teamIdが見つかりませんでした ", location()

    if request != None and request.json != None and request.json['title'] != None:
        msg = urllib.parse.unquote(request.json['title'], encoding='shift-jis')
    elif data != None and data.get('title') != None:
        msg = urllib.parse.unquote(data.get('title'), encoding='shift-jis')
    else:
        print("msgが見つかりません ", location())
        resMsg = "msgが見つかりません ", location()

    resStatus = ""

    if resMsg == "":
        print("msg: ", msg)
        req = tweet_v2(teamId, msg)
        # 汎用メソッドでレスポンスからデータを取り出す
        resData = content_by_req(req)
        if resData:
            resMsg = "Success: " + tuple_str(location())
            resStatus = 200
        else:
            resMsg = "Error: " + tuple_str(location())
            resStatus = 500
    else:
        resStatus = 500
    
    response = setResponse(resStatus, resMsg)
    return response

"""
検索ワードからツイートを検索します
→ファボに使う
[DEF]30件ファボしたら終わる
Javaから呼んでます
API V1.1しかできない。v2はfavしたいユーザーIDが必要
https://qiita.com/masaibar/items/e3b6911aee6741037549#%E5%8F%97%E3%81%91%E5%8F%96%E3%81%A3%E3%81%9F%E3%83%91%E3%83%A9%E3%83%A1%E3%83%BC%E3%82%BF%E3%82%92%E5%88%A9%E7%94%A8%E3%81%99%E3%82%8B
"""
@route('/twSearch', method='GET')
def twitter_search():
    resMsg = ""
    status = ""
    word = request.query.get('q')
    teamId = request.query.get('teamId')

    print("*** twitter_search() START ", "word=", word, " teamId=", teamId, " ***")

    count = 0

    # Tw API verをチェックし処理分岐
    apiVer2 = twApiVer2(teamId)
    if apiVer2:
        url = "https://api.twitter.com/2/tweets/search/recent?query=" + word
    else:
        url = "https://api.twitter.com/1.1/search/tweets.json?q=" + word

    if resMsg == "":
        activeAccount = oauthByTeamId(teamId)
        req = activeAccount.get(url)

        # 汎用メソッドでレスポンスからデータを取り出す
        resJson = content_by_req(req)
        print(resJson)
        if resJson:
            tmpResponse = ''
            if apiVer2:
                if resJson['data']:
                    for item in resJson['data']:
                        tmpResponse = like_v2(teamId, item["id"])  
                        if tmpResponse.status_code == 200:
                            print(item["id"] + " Success teamId=" + teamId, " count:", count)
                            count = count + 1
                        elif tmpResponse.status_code == (429 or 403):
                            print("Error: " + tmpResponse.status_code + ". Break transaction.")
                            resMsg = "Error: " + tmpResponse.status_code + ". Break transaction."
                            status = tmpResponse.status_code
                        if count >= 30:
                            break
            else:
                if resJson["statuses"]:
                    for item in resJson["statuses"]:
                        tmpResponse = like_v2(teamId, item["id_str"])
                        if tmpResponse.status_code == 200:
                            print(item["id_str"] + " Success teamId=" + teamId, " count:", count)
                            count = count + 1
                        elif tmpResponse.status_code == (429 or 403):
                            print("Error: " + tmpResponse.status_code + ". Break transaction.")
                            resMsg = "Error: " + tmpResponse.status_code + ". Break transaction."
                            status = tmpResponse.status_code
                        if count >= 30:
                            break
                    resMsg = "ファボしました"
                    status = req.status_code
                else:
                    print("検索結果が0件でした", "word=", word, " teamId=", teamId)
                    resMsg = "検索結果が0件でした", "word=", word, " teamId=", teamId
                    status = req.status_code
        else:
            print ("Error: %d" % req.status_code, location(), " ", content_by_req(req))
            response = setResponse(req.status_code, "検索結果が0件でした", "word=", word, " teamId=", teamId)
            resMsg = "エラーです"
            status = 500

    response = setResponse(status, resMsg)
    print("*** twitter_search() END ***")
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
        res = content_by_req(req)
        errCode = res["errors"][0]["code"]
        if errCode == 160:
            print("フォロリクsent: ", userToFollow)
            resCode = 200
    else:
        print ("フォロバError: %d" % req.status_code, userToFollow, location(), str(req))
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
        followingRes = content_by_req(req2)
    else:
        print ("フォローしてる人 get error: %d" % req2.status_code, location(), str(req2))


    # フォロワーを検索します
    req = activeAccount.get(url_followers)
    # レスポンスを確認
    if req.status_code == 200 or 201:
        followerRes = content_by_req(req)
    else:
        print ("フォロワー get error: %d" % req.status_code, location(), str(req))

    # フォローしてる人の中に入っていないフォロワーは今回Jobでのフォロー対象
    followTargetArr = []
    if apiVer2:
        followingUserId = []
        if followingRes["data"]:
            for userId in followingRes["data"]:
                followingUserId.append(userId["id"])

        followerUserId = []
        if followerRes["data"]:
            for userId in followerRes["data"]:
                followerUserId.append(userId["id"])

        if followerUserId:
            for twiId in followerUserId:
                if twiId not in followingUserId:
                    followTargetArr.append(twiId)
    else:
        if followerRes['ids']:
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
私のツイートをファボ/リツイ/リプしてくれた人の最新の投稿（ランダムx件）にいいねをつけに行きます
メソッドは作ったけどまだ使用なし
改善の余地あり（エラーチェック、意外と該当Tweetが取得できなかった時にまた上に戻るとか）
"""
@route('/engage', method='GET')
def engageWithReactors(argAsTeamId=0):
    teamId = request.query.get('teamId')

    # 外部からでなく内部からでも呼べるようにとArg1からTeamIdを取得する処理も入ってる
    if not teamId:
        teamId = argAsTeamId

    #自アカウントの投稿を集めます
    accountId = twitterIdByTeamId(teamId)
    fstPageFlg = True
    nextPageToken = ""
    checkTweet = []
    continueFlg = True

    activeAccount = oauthByTeamId(teamId)

    while continueFlg:
        if fstPageFlg:
            url = "https://api.twitter.com/2/users/" + accountId + "/tweets?tweet.fields=public_metrics,created_at&exclude=retweets&max_results=30"
        else:
            url = "https://api.twitter.com/2/users/" + accountId + "/tweets?tweet.fields=public_metrics,created_at&exclude=retweets&max_results=30&pagination_token=" + nextPageToken

        req = activeAccount.get(url)

        resJson = content_by_req(req)
        if 'data' in resJson.keys():
            dataArr = resJson['data']

        # リアクションのあるツイートIDを集めます
        if dataArr:
            for data in dataArr:
                if data['public_metrics']['retweet_count'] > 0 or data['public_metrics']['reply_count'] > 0 or data['public_metrics']['like_count'] > 0 or data['public_metrics']['quote_count'] > 0:
                    if data['id'] not in checkTweet:
                        checkTweet.append(data['id'])
                        print("****************checkTweet APPEND", len(checkTweet), location())

            # 次のページがあるようであればcontinue,ないならend
            if 'next_token' in resJson.keys():
                if resJson['meta'] and resJson['meta']['next_token'] and len(checkTweet) < 10:
                    nextPageToken = resJson['meta']['next_token']
            else:
                nextPageToken = ""
                continueFlg = False

        # 取得Tweetが10件あればend
        if len(checkTweet) > 10:
            continueFlg = False

    # リアクションのあるツイートがあったら、それぞれのツイートをlikeしてる人を確認します
    if checkTweet:
        print("checkTweetの中身:", checkTweet, location())
        liking_users = []
        for tweet in checkTweet:
            # Likeしてる人のリストを取得
            url2 = "https://api.twitter.com/2/tweets/" + tweet + "/liking_users?user.fields=entities,id,location,name,pinned_tweet_id,protected,public_metrics,url,username,verified,withheld"
            req2 = activeAccount.get(url2)
            resJson2 = content_by_req(req2)

            if 'data' in resJson2.keys():
                dataArr2 = resJson2['data']
                if dataArr2:
                    for data2 in dataArr2:
                        if data2["id"] not in liking_users:
                            liking_users.append(data2["id"])
        
        # likeしているユーザーIDを取得したらそのユーザーの投稿をlikeしに行く
        if liking_users:
            print("liking_users:", liking_users, location())
            for user in liking_users:
                # そのユーザーの投稿を5件取得
                url3 = "https://api.twitter.com/2/users/" + user + "/tweets?tweet.fields=public_metrics,created_at&exclude=retweets&max_results=5"
                req3 = activeAccount.get(url3)
                resJson3 = content_by_req(req3)
                if 'data' in resJson3.keys():
                    dataArr3 = resJson3['data']
                    if dataArr3:
                        count = 0
                        for data3 in dataArr3:
                            # 2件likeを試みる
                            if count < 3:
                                url4 = "https://api.twitter.com/2/users/" + accountId + "/likes"
                                data4 = {"tweet_id": data3["id"]}
                                req4 = activeAccount.post(url4, data = json.dumps(data4))
                                print("likeしました:", data3["id"], vars(req4))
                                count = count + 1
                            else:
                                break
                else:
                    print(resJson3, location())

    return "OK"

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
            print("General", teamId)
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
