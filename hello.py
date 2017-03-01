#!/usr/bin/env python
import tweepy
import random
import json

#from our keys module (keys.py), import the keys dictionary
from keys import keys
CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

twt = api.search(q="@censusPlaces")

#list of specific strings we want to check for in Tweets
t = ['@censusPlaces 1',
'@censusPlaces 2',
'@censusPlaces 3',
'@censusPlaces 4',
'@censusPlaces 5',
'@censusPlaces 6',
'@censusPlaces 7'
]

s = twt[0]
   # if s["coordinates"]:
    #    print s[coordinates]
print s.geo
sn = s.user.screen_name
m = " @%s Hello!" % (sn)+str(s.geo["coordinates"])
s = api.update_status(m, s.id)

c = s.coordinates
json_s = json.dumps(s._json)
