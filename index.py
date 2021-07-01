# -*- coding: utf-8 -*-
import os, twitter, urllib.parse
from bottle import TEMPLATES, route, run, post, request, HTTPResponse
from datetime import datetime

@route("/")
def hello_world():
    return "Hello"

@route("/hola")
def hello():
    return "Hola"

@route('/twi/<msg>')
def twitter(msg):
    import twitter
    api = twitter.Api(consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token_key=os.environ["ACCESS_TOKEN_KEY"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    api.PostUpdate(msg)
    return "Tweeted"

@route('/twi', method='POST')
def twitter_post():
    import twitter
    api = twitter.Api(consumer_key=os.environ["CONSUMER_KEY"],
        consumer_secret=os.environ["CONSUMER_SECRET"],
        access_token_key=os.environ["ACCESS_TOKEN_KEY"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    title = request.json['title']
    try:
        api.PostUpdate(urllib.parse.unquote(title, encoding='shift-jis'))
    except twitter.TwitterError as e:
        print(e)
        return HTTPResponse(status=201)
    except Exception as e:
        print(e)
        return HTTPResponse(status=500)

    return HTTPResponse(status=201)

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
