from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import date, datetime
import urllib.request
import config
import re
import logging
from datetime import datetime
from bottle import route, run
import os
 
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

# driver = webdriver.Chrome(ChromeDriverManager().install())
options = Options()
# options = webdriver.ChromeOptions()
# options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
options.binary_location = '/app/.chromedriver/bin'
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1200x600')

# # サービスの起動
# service = Service(executable_path='/usr/local/bin/chromedriver-helper')
# try:
#     service.start()
#     # Chrome に接続
#     driver = webdriver.Remote(service.service_url, desired_capabilities=options.to_capabilities())
# except Exception as e:
#     logger.error(e)

def insertTvRecord(data):
    url = 'http://160.251.22.190/postTvProgram'
    print(str(data))

    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    # response = urllib.request.urlopen(req, json.dumps(data).encode())
    urllib.request.urlopen(req, json.dumps(data).encode())
    # with response as res:
    #     body = res.read()
    #     print(body)

def post(data):
    url = 'http://localhost:5000/twi'

    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    urllib.request.urlopen(req, json.dumps(data).encode())

def findIdByKey(key):
    for arr in config.teams.all_teams_array:
        i = 0
        while i < len(arr):
            if key in str(arr[i]):
                return arr[0]
            else:
                i += 1
    return 0

url = 'https://tv.yahoo.co.jp/listings'

@route("/main")
def cron():
    # サービスの起動
    service = Service(executable_path='/usr/local/bin/chromedriver-helper')
    try:
        service.start()
        # Chrome に接続
        driver = webdriver.Remote(service.service_url, desired_capabilities=options.to_capabilities())
    except Exception as e:
        logger.error(e)
    # Webページを読み込み、htmlを取得して、beautifulSoupでパース
    # driver.set_window_position(-10000,0)
    try:
        driver.get(url)
    except Exception as e:
        logger.error(e)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html,'html.parser')

    # 番組表情報の取得
    # soupdate = soup.find('div', class_='listingOptionWrap').find('option', {'selected': True})
    today = datetime.strptime(str(date.today()), '%Y-%m-%d')

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
    # print(channel_list)

    # 番組タイトルを含む要素の取得
    # title_elems = soup.find_all('a', class_='listingTablesTextLink')

    # アーティスト名リスト
    key_list = []
    for arr in config.teams.all_teams_array:
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
                    store.append([key, channel_list[int(channel_index)-1], str(today.strftime('%Y/%m/%d')) + " " + e.find('span', class_='ListingTimeOut').text, e.find('a', class_='listingTablesTextLink').text, e.find('p', class_='listingTablesTextDescription').text, program_id])
                    break

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
            return data
            # insertTvRecord(data)

            # ポストする
            # title = "今日（" + str(today.strftime('%m/%d')) + "）のTV出演情報です%0A%0A" + e[2] + " " + e[1][1] + "%0A" + e[3] + "%0A" + e[4]
            # # url = 'http://localhost:5000/twi'
            # team_id = findIdByKey(e[0])
            # post_data = {
            #     'teamId': team_id,
            #     'title': title
            # }

            # post(post_data)

@route("/yahoo")
def yahoo():
    # return str(station_elems)
    return "hello"

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))