app_name = "pytwi2"

consumer_key = "J97obYNcAFauZIndYTa6h7Lwm" # アプリケーション管理画面のConsumer API Keys > API key
consumer_secret = "yc1k2zis9E53vPv5wlVrSnTsML2X9Z2b2eU8mxI5sSR0pvGRYZ"  # アプリケーション管理画面のConsumer API Keys > API secret key
token = "1409384870745313286-9yPpw6az93vCyGEK1JJGX0DgNbm7SX"
token_secret = "3GZqtD6NoWtwLMr43gKVYtcTqVjMfeI3Ig3pRK4Y0RURE"

snowman_consumer_key="wVsD8xCkpMXIAdQ8dqidzVKWv"
snowman_consumer_secret = "DGe3lGA82F9MjRMvzEvrnM2ALWOudV56CeDdNfOq3lBmQU7dHs"  # アプリケーション管理画面のConsumer API Keys > API secret key
snowman_token = "1409169347277332481-W8q1hKoB3ojqRRbJU6HDbVzGLSyq9O"
snowman_token_secret = "4OOl0DC9OvDsttHdf13VcmhzQmysrPicSwIuk3LNrLkvs"

sixtones_consumer_key = "MPTKYhz7EkjeVNh4j0VR2C69w" # アプリケーション管理画面のConsumer API Keys > API key
sixtones_consumer_secret = "DpgcVnwGUuQHqwi5vAvZoMmpFjmFOUCdAUssZEIB86Zpo1V9JV"  # アプリケーション管理画面のConsumer API Keys > API secret key
sixtones_token = "1411427767443283969-MBBR0kluN2wuGpieJlTyWQSMlSaQFj"
sixtones_token_secret = "iqUBAe4T6VrJTpY9BXISOAyup1qd9ajW5fx6HpxLxrepe"

kinpri_consumer_key = "8xS3q8JsL8PUnTfUhNpH2nc4W" # アプリケーション管理画面のConsumer API Keys > API key
kinpri_consumer_secret = "8KRpUqYabSwHEAxmajDSD35ctPse2pXqqT6trShlkvyam8GEC3"  # アプリケーション管理画面のConsumer API Keys > API secret key
kinpri_token = "1411429221038116866-kcLXzQ3On9C4KtOwWxumEvF2urGg8R"
kinpri_token_secret = "ZkqmnfLt4ZWKEj268sPvuxSAkMbbw0cWGtVLXGLUBioWY"

class Teams:
    snowman=[6,"スノーマン",None,"Snow Man"]
    kanjani=[7,"カンジャニエイト","関ジャニ","関ジャニ∞"]
    sexyzone=[8,"セクシーゾーン","セクゾ","Sexy Zone"]
    tokio=[9,"トキオ",None,"TOKIO"]
    v6=[10,"ブイシックス",None,"V6"]
    arashi=[11,"アラシ","嵐","ARASHI"]
    # news=[12,"ニュース",None,"NEWS"]
    kismyft2=[13,"キスマイフットツー","キスマイ","Kis-My-Ft2"]
    abcz=[14,"エービーシーズィー","エビ","A.B.C-Z"]
    johnnyswest=[15,"ジャニーズウェスト","ジャニスト","ジャニーズWEST"]
    kingandprince=[16,"キングアンドプリンス","キンプリ","King & Prince"]
    sixtones=[17,"ストーンズ","ストンズ","SixTONES"]

    all_teams_array = [snowman, kanjani, sexyzone, tokio, v6, arashi, kismyft2, abcz, johnnyswest, kingandprince, sixtones]

# Yahoo TV
ENV='dev'
CHROME='/usr/local/bin/chromedriver-helper'
TWI_POST='http://localhost:5000/twi'
