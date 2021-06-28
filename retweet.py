# https://qiita.com/ucdj_marvel/items/cd61fd187d26c245e37d
import sys, os, tweepy

CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN_KEY"]
ACCESS_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

def fav_retweet(target_accounts):
    for target_ac in target_accounts:

        query = "from:" + target_ac
        search_results = api.search(q=query, count=5)

        for result in search_results:
            tweet_id = result.id
            user_id = result.user._json['id']
            try:
                api.create_favorite(tweet_id)
                api.retweet(tweet_id)
            except Exception as e:
                print(target_ac, e)
                break

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

fav_retweet(sys.argv)
