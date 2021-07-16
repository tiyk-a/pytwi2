from bs4 import BeautifulSoup
from selenium import webdriver   
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import date, datetime
import urllib.request
import config
import re

driver = webdriver.Chrome(ChromeDriverManager().install())

def insertTvRecord(data):
    url = 'http://localhost/postTvProgram'
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

# Webページを読み込み、htmlを取得して、beautifulSoupでパース
driver.set_window_position(-10000,0)
driver.get(url)
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html,'html.parser')

# 番組表情報の取得
soupdate = soup.find('div', class_='listingOptionWrap').find('option', {'selected': True})
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
title_elems = soup.find_all('a', class_='listingTablesTextLink')

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
        insertTvRecord(data)

        # ポストする
        title = "今日（" + str(today.strftime('%m/%d')) + "）のTV出演情報です%0A%0A" + e[2] + " " + e[1][1] + "%0A" + e[3] + "%0A" + e[4]
        url = 'http://localhost:5000/twi'
        team_id = findIdByKey(e[0])
        post_data = {
            'teamId': team_id,
            'title': title
        }

        post(post_data)
