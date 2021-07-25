# -*- coding: utf-8 -*-
import os, twitter, urllib.parse
from bottle import run, route, request, HTTPResponse

from twitter import *
from config import *

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
from datetime import date, datetime
import urllib.request
import re
import logging
from datetime import datetime

@route("/")
def hello_world():
    return "Hello"

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
            snowman.statuses.update(status=title)
        elif teamId == 17: # SixTONES
            sixtones.statuses.update(status=title)
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

"""
consoleハンドラをロガーに追加する
"""
# test用のロガーを取得し、consoleハンドラを追加する
logger = logging.getLogger(__name__)
logger.addHandler(console)
# datetime_module用のロガーを取得し、consoleハンドラを追加する。他に追加したいモジュールがあれば同じ形式で追加する
logging.getLogger("datetime_module").addHandler(console)
 
 
if __name__ == '__main__':
 
    datetime_now = datetime.now()

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1200x600')

def insertTvRecord(data):
    url = 'http://160.251.22.190/postTvProgram'
    print(str(data))

    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req, json.dumps(data).encode())

def findIdByKey(key):
    for arr in Teams.all_teams_array:
        i = 0
        while i < len(arr):
            if key in str(arr[i]):
                return arr[0]
            else:
                i += 1
    return 0

"""
データを探します。
search_url=検索先画面URL
dateStr=検索日（string）、検索には不使用、DB保存の日付に使用
recurseFlg=別日も続けて検索するかflag
"""
@route("/tv")
def cron(search_url, dateStr, recurseFlg):
    print("検索開始　search_url: ", search_url, "dateStr: ", dateStr,"recurseFlg: ", recurseFlg)
    # サービスの起動
    service = Service(executable_path=CHROME)
    try:
        service.start()
        # Chrome に接続
        driver = webdriver.Remote(service.service_url, desired_capabilities=options.to_capabilities())
    except Exception as e:
        logger.error(e)
    # Webページを読み込み、htmlを取得して、beautifulSoupでパース
    try:
        driver.get(search_url)
    except Exception as e:
        logger.error(e)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html,'html.parser')

    """
    その日の情報を取得
    """
    # 番組表の上部に書かれているチャンネルリストの取得
    station_elems = soup.find_all('td', class_='listingTablesChannelItem')
    channel_list = []
    for e in station_elems:
        num = e.find('span', class_='listingNumber')
        channel = e.find('span', class_='listingChannelItem')

        if num != None:
            num = num.text
        if channel != None:
            channel = channel.text
        else:
            channel = e.find('option', class_='listingChannelSelecterOption')
            if channel != None:
                channel = channel.text
        channel_list.append([num, channel])

    # アーティスト名リスト
    key_list = []
    for arr in Teams.all_teams_array:
        key_list.append(arr[3])
        key_list.append(arr[2])
        key_list.append(arr[1])

    # 合致した番組を入れていく
    store = []

    td_elems = soup.find_all('td', class_='listingTablesItem')
    for e in td_elems:
        for key in key_list:
            if key != None:
                regex = '(<td class=\"listingTablesItem\")(.*)(' + key + ')(.*)(</button></td>)'
                if re.fullmatch(regex, str(e)) != None:
                    site_json=json.loads(e.find('a', class_='listingTablesTextLink').attrs['data-tracking'])
                    channel_index = site_json.get("pos")
                    program_id = e.find('a', class_='listingTablesTextLink').attrs['href'].strip('/program/')
                    store.append([key, channel_list[int(channel_index)-1], dateStr + " " + e.find('span', class_='ListingTimeOut').text, e.find('a', class_='listingTablesTextLink').text, e.find('p', class_='listingTablesTextDescription').text, program_id])
                    break

    # 検索結果データが1件以上あれば
    if len(store) > 0:
        for e in store:
            # DB保存する
            data = {
                'station': e[1][1],
                'program_code': e[5],
                'title': e[3],
                'description': e[4],
                'on_air_date': e[2],
                'keyword':e[0]
            }
            print(data)
            if ENV == 'production':
                insertTvRecord(data)
    
    # 再帰フラグがTrueなら続けて調べるための日付とURLを調べる
    if recurseFlg:
        """
        他の日付の情報も探したいからパラメタを探す
        """
        cal_links = soup.find_all('a', class_='calendarListingListItemLink')
        cal_dates = soup.find_all('h2', class_='calendarListingListItemTitle')
        date_link = {}
        for e in cal_dates:
            date_link[e.find('time')['datetime']] = cal_links[cal_dates.index(e)]['href']
        
        # 今日のはもう取得済みなのでリストから削除する
        dateStrArr = dateStr.split("-")
        if dateStrArr[1][0] == "0":
            dateStrArr[1] = dateStrArr[1][1]
        if dateStrArr[2][0] == "0":
            dateStrArr[2] = dateStrArr[2][1]
        dateStr = dateStrArr[0] + "-" + dateStrArr[1] + "-" + dateStrArr[2]
        date_link.pop(dateStr)
        return date_link

"""
TV番組検索指示を出します。
①本日の番組を検索
②続いて翌日以降の番組を検索（翌日と、その先2日にいっぺんずつ）
"""
@route("/search")
def today_search():    
    """
    今日のテレビ欄を検索する
    """
    url = 'https://tv.yahoo.co.jp/listings'
    future_date_links = cron(url, datetime.today().strftime('%Y-%m-%d'), True)

    """
    未来の日付のリンクも取得できたら検索しにいく。
    returnされたものは受け取らない。
    """
    if len(future_date_links) > 0:
        count = 0;
        for k,v in future_date_links.items():
            if count%2 == 0:
                date_split = k.split("-")
                if len(date_split[1]) == 1:
                    k = date_split[0] + "-0" + date_split[1] + "-" + date_split[2]
                elif len(date_split[2]) == 1:
                    k = date_split[0] + "-" + date_split[1] + "-0" + date_split[2]

                cron("https://tv.yahoo.co.jp" + v, datetime.strptime(k, '%Y-%m-%d').strftime('%Y-%m-%d'), False)
            count+=1

@route("/env")
def yahoo():
    return ENV

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
