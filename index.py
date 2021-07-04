# -*- coding: utf-8 -*-
import os, twitter, urllib.parse
from bottle import run, route, request, HTTPResponse

from twitter import *
from config import *
@route("/")
def hello_world():
    return "Hello"

@route("/hola")
def hello():
    return "Hola"

@route('/twi', method='POST')
def twitter_post():

    # Snowman Account
    snowman = Twitter(
        auth=OAuth(
            snowman_token,
            snowman_token_secret,
            snowman_consumer_key,
            snowman_consumer_secret,
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

    teamId = request.json['teamId']
    title = urllib.parse.unquote(request.json['title'], encoding='shift-jis')
    try:
        if teamId == 0: # N/A -> General Account
            t.statuses.update(status=title)
            snowman.statuses.update(status=title)
        elif teamId == 6: # Snowman
            snowman.statuses.update(status=title)
        elif teamId == 7: # 関ジャニ∞
            t.statuses.update(status=title)
        elif teamId == 8: # Sexy Zone
            t.statuses.update(status=title)
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
            t.statuses.update(status=title)
        else: # General Account
            t.statuses.update(status=title)
    except twitter.TwitterError as e:
        print(e)
        return HTTPResponse(status=201)
    except Exception as e:
        print(e)
        return HTTPResponse(status=500)

    return HTTPResponse(status=201)

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
