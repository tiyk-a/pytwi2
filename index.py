# -*- coding: utf-8 -*-
import os, twitter, urllib.parse
from bottle import run, route, request, HTTPResponse

from twitter import *
from config import *

import urllib.request
import logging

@route("/")
def hello_world():
    return 'Hello', 200

@route('/twi', method='POST')
def twitter_post(data=None):

    # Snowman Account
    snowman = Twitter(
        auth=OAuth(
            snowman_token,
            snowman_token_secret,
            snowman_consumer_key,
            snowman_consumer_secret,
        )
    )

    # SixTONES Account
    sixtones = Twitter(
        auth=OAuth(
            sixtones_token,
            sixtones_token_secret,
            sixtones_consumer_key,
            sixtones_consumer_secret,
        )
    )

    # King & Prince Account
    kinpri = Twitter(
        auth=OAuth(
            kinpri_token,
            kinpri_token_secret,
            kinpri_consumer_key,
            kinpri_consumer_secret,
        )
    )

    # なにわ男子 Account 
    naniwa = Twitter(
        auth=OAuth(
            naniwa_token,
            naniwa_token_secret,
            naniwa_consumer_key,
            naniwa_consumer_secret,
        )
    )

   # SexyZone Account 
    sexyzone = Twitter(
        auth=OAuth(
            sexyzone_token,
            sexyzone_token_secret,
            sexyzone_consumer_key,
            sexyzone_consumer_secret,
        )
    )

    # General Account
    t = Twitter(
        auth=OAuth(
            token,
            token_secret,
            consumer_key,
            consumer_secret,
        )
    )

    if request != None and request.json != None and request.json['teamId'] != None and request.json['title']:
        teamId = request.json['teamId']
        title = urllib.parse.unquote(request.json['title'], encoding='shift-jis')
    elif data != None and data.get('teamId') != None and data.get('title') != None:
        teamId = data.get('teamId')
        title = urllib.parse.unquote(data.get('title'), encoding='shift-jis')
    else:
        print("Error")
    try:
        if teamId == 0: # N/A -> General Account
            t.statuses.update(status=title)
        elif teamId == 17: # SixTONES
            sixtones.statuses.update(status=title)
        elif teamId == 6: # Snowman
            snowman.statuses.update(status=title)
        elif teamId == 7: # 関ジャニ∞
            t.statuses.update(status=title)
        elif teamId == 8: # Sexy Zone
            sexyzone.statuses.update(status=title)
        elif teamId == 9: # TOKIO
            t.statuses.update(status=title)
        elif teamId == 10: # v6
            t.statuses.update(status=title)
        elif teamId == 11: # ARASHI
            t.statuses.update(status=title)
        elif teamId == 12: # NEWS
            t.statuses.update(status=title)
        elif teamId == 13: # Kis-My-Ft2
            t.statuses.update(status=title)
        elif teamId == 14: # A.B.C-Z
            t.statuses.update(status=title)
        elif teamId == 15: # ジャニーズWEST
            t.statuses.update(status=title)
        elif teamId == 16: # King & Prince
            kinpri.statuses.update(status=title)
        elif teamId == 18: # なにわ男子
            naniwa.statuses.update(status=title)
        else: # General Account
            t.statuses.update(status=title)
    except twitter.TwitterError as e:
        print(e)
        return HTTPResponse(status=201)
    except Exception as e:
        print(e)
        return HTTPResponse(status=500)

    return HTTPResponse(status=201)

LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'
 
# フォーマットを指定 (https://docs.python.jp/3/library/logging.html#logrecord-attributes)
_detail_formatting = '%(asctime)s %(levelname)-8s [%(module)s#%(funcName)s %(lineno)d] %(message)s'
 
 
"""
LOG_LEVEL_FILEレベル以上のログをファイルに出力する設定
"""
# datetime_moduleモジュールを呼び出す側(test.py)で出力形式などの基本設定をする
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL_FILE), # LOG_LEVEL_FILE = 'DEBUG' なら logging.DEBUGを指定していることになる
    format=_detail_formatting,
    filename='./logs/yahoo.log'
)

console = logging.StreamHandler()
console.setLevel(getattr(logging, LOG_LEVEL_CONSOLE)) # LOG_LEVEL_CONSOLE = 'INFO' なら logging.INFOを指定していることになる
console_formatter = logging.Formatter(_detail_formatting)
console.setFormatter(console_formatter)

@route("/env")
def yahoo():
    return ENV

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
