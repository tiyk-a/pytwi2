# https://qiita.com/enomotok/items/41275dd904c8aa774e72#procfile

# Twitter Posting App

## 機能一覧
* Twitterポスト
  * リクエストが飛んできたら任意のアカウントにポスト
* Yahoo!番組表のスクレイピング←使用してるか不明？
  * キーワードの含まれる番組データを抽出
    * →ConoHa側に飛ばしてDB保存
* Favorite機能
  * 引数1で受けた投稿をファボします。すでにファボしていたらエラーを吐きます
  * ファボするアカウントは引数2
* キーワード検索→ファボ（30件するまで終わらない）
  * 引数1で渡されたキーワードで検索（最新x人気）し、その結果をファボする機能に受け渡します
  * 検索＆ファボするアカウントは引数2
* フォロバ機能
  * 引数1で受けたユーザーを引数2のユーザーがフォローします
* フォロバしてないユーザー検知→フォロバ
  * (フォローされているユーザー)-(フォローしているユーザー)を確認し、フォロバしていなかったらフォロバ機能に飛ばします

# テストの方法
`https://pytwi2.herokuapp.com/twi`
上記URLにPOSTでデータを送ると、該当Twitterにポストされるはず。
```
{
  "title": "apptest",
  "teamId": 7,
}
```
上のデータの場合、"apptest"という文字列がジャニ総合アカウントにポストされるはず

# 本番環境
* heroku
* Job
停止中
```
$ python retweet.py Infinity_rJP arashi5official kingandprince_j tokioinc_taichi smileup_project islandtv_up J_DREAMIsLAND
```