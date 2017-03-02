import tweepy
import os
import oauth2, time, urllib, urllib2, json
from functools import partial
import random
import pprint
import csv
import math
import json
from math import radians, cos, sin, asin, sqrt
from shapely.geometry import *
from shapely.ops import cascaded_union
from operator import itemgetter
import time
from datetime import datetime
# Authentication details. To  obtain these visit dev.twitter.com
consumer_key = 'o9b6vjM8hs0iTzQkSA8oMUN7Y'
consumer_secret = 'Sj7SdfPtknaIAN5d9yyJqaqp7RpmWqMiZeTfDrPHRxEfNbT0Ek'
access_token = '3332909505-49Zu2S9P9ZAh09SFE3G93D653RSpDjqSseKTXEf'
access_token_secret = 'omCvhWovaxUttfAbtNn22XCQrYvlY4z7pGYllR5w4Nr68'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def getId(lng,lat):
    point = Point(float(lng),float(lat))
    with open("data/ny_ma.geojson") as f:
        js =json.load(f)
        for i in range(len(js['features'])):
            feature = js['features'][i]
            uid = feature["properties"]["GEOID"]
            polygon = shape(feature['geometry'])
            if polygon.contains(point)==True:
                print uid
                return uid
def convertToSentence(key,value):    
    dataDictionaryTranslateFile = open("data/socialExplorer_dictionary_translate.json")
    dataDictionaryTranslate = json.load(dataDictionaryTranslateFile)
    sentence = dataDictionaryTranslate[key].replace("XXX",value)
    return sentence
def shortenSentences(sentences):
    pick3 = random.sample(sentences, 3)
    sentence = "you are at"+" at a place where "+pick3[0]+", "+pick3[1]+", and "+pick3[2]+"."
    return sentence
def getData(bgid):
    dataByIdFile = open("data/socialExplorer_data.json")
    dataById =json.load(dataByIdFile)
    
    dataDictionaryFile = open("data/socialExplorer_dictionary.json")
    dataDictionary = json.load(dataDictionaryFile)
    
    dataDictionarySelectedFile = open("data/socialExplorer_dictionary_selected.json")
    dataDictionarySelected = json.load(dataDictionarySelectedFile)
    
    selectedKeys = dataDictionarySelected.keys()
    sentenceDictionary = {}
    sentences = []
    
   # print dataById[bgid]
    
    for key in dataDictionary:
        if key in selectedKeys:
            if key.split("_")[1]!="001" and key!="T002_002":
                    totalKey = key.split("_")[0]+"_001"
                  #  print totalKey
                   # print dataById[bgid]["SE_"+str(totalKey)]
                    total = float(str(dataById[bgid]["SE_"+str(totalKey)]))
                    if total != 0 and str(dataById[bgid]["SE_"+str(key)])!=0:
                       # print str(dataById[bgid]["SE_"+str(key)])
                        value = int(float(str(dataById[bgid]["SE_"+str(key)])))
                        
                        percentage = str(round(int(str(value))/total*10000)/100)+"%"
                        if percentage == "0.0%":
                            percentage = "0%" 
                        #print key, dataDictionary[key]
                        #print total, value, percentage
                        sentence = convertToSentence(key,percentage)
                        sentences.append(str(sentence))
            elif dataById[bgid]["SE_"+str(key)]!="":
                value = str(int(round(float(str(dataById[bgid]["SE_"+str(key)])))))
                #print key, dataDictionary[key],value
                sentence = convertToSentence(key,value)
                sentences.append(str(sentence))
                
            sentenceDictionary[key]=sentence
    return shortenSentences(sentences)
# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)

        user = decoded['user']['screen_name']
        userId = decoded["id"]
        
        if user!="censusPlaces":
            if decoded["coordinates"] == None:
                message = "@"+user+" share precise location is not enabled on your tweet. Please turn it on at bottom of screen and try again."
                api.update_status(message)
            else:
                if decoded["coordinates"]["coordinates"]==None:
                    message = "@"+user+" share precise location is not enabled on your tweet. Please turn it on at bottom of screen and try again."
                    api.update_status(message)
                else:
                    coordinates = decoded["coordinates"]["coordinates"]
                    lng = coordinates[0]
                    lat = coordinates[1]
                    bgid = getId(lng,lat)
                    if bgid == None:
                        message = "@"+user+" I'm so sorry, you are outside of my current dataset, please check back in a few days :("
                        api.update_status(message)
                    else:
                        sentence = getData(bgid)
                        message = "@"+user+" "+sentence
                        if len(message)>140:
                            message = message[0:135]+"..."
                        api.update_status(message,userId)
            
        print decoded.keys()
        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
        print message
        #print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        print ''
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
#    test coordinates with these    
#    coordinates = [42.225405, -73.289938]
#    lng = coordinates[1]
#    lat = coordinates[0]
#    bgid = getId(lng,lat)
#    sentence = getData(bgid)
#    print "tester", sentence
    
    
    # There are different kinds of streams: public stream, user stream, multi-user streams
    # In this example follow #programming tag
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    stream = tweepy.Stream(auth, l)
    stream.filter(track=['@censusPlaces'])
    

