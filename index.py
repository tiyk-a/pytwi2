# -*- coding: utf-8 -*-
import os, twitter, urllib.parse
from bottle import TEMPLATES, route, run, post, request, HTTPResponse
from datetime import datetime

from twitter import *
from config import *
@route("/")
def hello_world():
    return "Hello"

@route("/hola")
def hello():
    return "Hola"

# @route('/twi/<msg>')
# def twitter(msg):
#     import twitter
#     api = twitter.Api(consumer_key=os.environ["CONSUMER_KEY"],
#         consumer_secret=os.environ["CONSUMER_SECRET"],
#         access_token_key=os.environ["ACCESS_TOKEN_KEY"],
#         access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
#     )
#     api.PostUpdate(msg)
#     return "Tweeted"

@route('/twi', method='POST')
def twitter_post():
    # import twitter
    # api = twitter.Api(consumer_key=os.environ["CONSUMER_KEY"],
    #     consumer_secret=os.environ["CONSUMER_SECRET"],
    #     access_token_key=os.environ["ACCESS_TOKEN_KEY"],
    #     access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    # )
    snowman = Twitter(
        auth=OAuth(
            snowman_token, # token（config.txtの1行目）
            snowman_token_secret, # token_secret（config.txtの2行目）
            snowman_consumer_key,
            snowman_consumer_secret,
        )
    )
    t = Twitter(
        auth=OAuth(
            token, # token（config.txtの1行目）
            token_secret, # token_secret（config.txtの2行目）
            consumer_key,
            consumer_secret,
        )
    )
    teamId = request.json['teamId']
    title = request.json['title']
    try:
        if teamId == 0:
            t.statuses.update(status=urllib.parse.unquote(title + "ue", encoding='shift-jis'))
            snowman.statuses.update(status=urllib.parse.unquote(title + "shita", encoding='shift-jis'))
        # elif teamId == 1:
        #     t.statuses.update(status=urllib.parse.unquote(title + "ue", encoding='shift-jis'))
        elif teamId == 6:
            snowman.statuses.update(status=urllib.parse.unquote(title + "ue", encoding='shift-jis'))
        else:
            t.statuses.update(status=urllib.parse.unquote(title + "ue", encoding='shift-jis'))
    except twitter.TwitterError as e:
        print(e)
        return HTTPResponse(status=201)
    except Exception as e:
        print(e)
        return HTTPResponse(status=500)

    return HTTPResponse(status=201)

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
