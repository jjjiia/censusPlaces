#censusPlaces
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
print "running with all packages"
#bot
#take whole api data with ids
def getData(bgid):
    locations = open("data/openpaths_jjjiia_withgid.csv","r")
    locationsReader = csv.reader(locations)
    next(locationsReader, None)
    dataByIdFile = open("data/socialExplorer_data.json")
    dataById =json.load(dataByIdFile)
    
    dataDictionaryFile = open("data/socialExplorer_dictionary.json")
    dataDictionary = json.load(dataDictionaryFile)
    
    dataDictionarySelectedFile = open("data/socialExplorer_dictionary_selected 2.json")
    dataDictionarySelected = json.load(dataDictionarySelectedFile)
    
    selectedKeys = dataDictionarySelected.keys()
    sentenceDictionary = {}
    sentences = []
    
    for key in dataDictionary:
        if key in selectedKeys:
            if key.split("_")[1]!="001" and key!="T002_002":
                    totalKey = key.split("_")[0]+"_001"
                    total = float(str(dataById[bgid]["SE_"+str(totalKey)]))
                    if total != 0:
                        value = int(float(str(dataById[bgid]["SE_"+str(key)])))
                        percentage = str(round(int(str(value))/total*10000)/100)+"%"
                        if percentage == "0.0%":
                            percentage = "0%" 
                        #print key, dataDictionary[key]
                        #print total, value, percentage
                        sentence = convertToSentence(key,percentage)
                        sentences.append(str(sentence))
            else:
                value = str(int(round(float(str(dataById[bgid]["SE_"+str(key)])))))
                #print key, dataDictionary[key],value
                sentence = convertToSentence(key,value)
                sentences.append(str(sentence))
                
            sentenceDictionary[key]=sentence
    #print sentences
    return shortenSentences(sentences)
    return sentences
    
def getTime():
    print "time"
    
def shortenSentences(sentences):
    pick3 = random.sample(sentences, 3)
    sentence = "J spent the last "+"TTTTTTTT"+" at a place where "+pick3[0]+", "+pick3[1]+", and "+pick3[2]+"."
    return sentence
    
def convertToSentence(key,value):    
    dataDictionaryTranslateFile = open("data/socialExplorer_dictionary_translate.json")
    dataDictionaryTranslate = json.load(dataDictionaryTranslateFile)
    sentence = dataDictionaryTranslate[key].replace("XXX",value)
    return sentence

#match categories
#compose tweet
#calculate time
def formatTimePassed(timePassed):
    if timePassed>=60:
        return str(int(float(timePassed)/60)) +" hrs "
    else:
        return str(timePassed)+" mins "
#date
def timeLapsed(timestamp1,timestamp2):
    fmt = '%Y-%m-%d %H:%M:%S'
    a = datetime.strptime(timestamp1,fmt)
    b = datetime.strptime(timestamp2,fmt)
    secondsLapsed = ((a-b).total_seconds())
    print secondsLapsed
    time.sleep(secondsLapsed)
    return secondsLapsed 
    
def formatTimeLapsed(seconds):
    if seconds > 60 and seconds<60*60:
        return str(int(round(seconds/60)))+"mins"
    elif seconds >= 60*60 and seconds < 60*60*24:
        return str(int(round(seconds/60/60)))+" hrs"
    elif seconds>60*60*24:
        return str(int(round(seconds/60/60/24)))+" days"
    
#tweet
class EverywordBot(object):

    def __init__(self, consumer_key, consumer_secret,
                 access_token, token_secret,
                 source_file_name, index_file_name,
                 lat=None, long=None, place_id=None,
                 prefix=None, suffix=None, bbox=None):
        self.source_file_name = source_file_name
        self.index_file_name = index_file_name
        self.lat = lat
        self.long = long
        self.place_id = place_id
        self.prefix = prefix
        self.suffix = suffix
        self.bbox = bbox

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, token_secret)
        self.twitter = tweepy.API(auth)

    def _get_current_index(self):
        if not(os.path.isfile(self.index_file_name)):
            return 0
        with open(self.index_file_name) as index_fh:
            return int(index_fh.read().strip())

    def _increment_index(self, index):
        with open(self.index_file_name, "w") as index_fh:
            index_fh.truncate()
            index_fh.write("%d" % (index + 1))
            index_fh.close()

    def _get_current_line(self, index):
        with open(self.source_file_name) as source_fh:
            # read the desired line
            for i, status_str in enumerate(source_fh):
                if i == index:
                    break
            return status_str.strip()

    def _random_point_in(self, bbox):
        """Given a bounding box of (swlat, swlon, nelat, nelon),
         return random (lat, long)"""
        import random
        lat = random.uniform(bbox[0], bbox[2])
        long = random.uniform(bbox[1], bbox[3])
        return (lat, long)

    def post(self):
        
        index = self._get_current_index()
        fileLine = self._get_current_line(index).split(",")
        previousLine = self._get_current_line(index-1).split(",")
        self._increment_index(index)
        
        time = fileLine[3]
        lastTime = previousLine[3]
        secondsLapsed = timeLapsed(time, lastTime)
        timeFormated = formatTimeLapsed(secondsLapsed)
        
        #print secondsLapsed, timeFormated
        bgid = fileLine[8]
        tweetSentence = getData(bgid).replace("TTTTTTTT",timeFormated)
        if len(tweetSentence)>139:
            tweetSentence = tweetSentence[0:135]+"..."
        status_str = tweetSentence
        print "status", status_str 
        
        if self.prefix:
            status_str = self.prefix + status_str
        if self.suffix:
            status_str = status_str + self.suffix
        if self.bbox:
            self.lat, self.long = self._random_point_in(self.bbox)

        self.twitter.update_status(status=status_str,
                                   lat=self.lat, long=self.long,
                                   place_id=self.place_id)
        self._increment_index(index)
        
for i in range(10000):
    if __name__ == '__main__':

        def _get_comma_separated_args(option, opt, value, parser):
            setattr(parser.values, option.dest, _csv_to_float_list(value))

        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option('--consumer_key', dest='consumer_key',
                          help="twitter consumer key")
        parser.add_option('--consumer_secret', dest='consumer_secret',
                          help="twitter consumer secret")
        parser.add_option('--access_token', dest='access_token',
                          help="twitter token key")
        parser.add_option('--token_secret', dest='token_secret',
                          help="twitter token secret")
        parser.add_option('--source_file', dest='source_file',
                          default="tweet_list.txt",
                          help="source file (one line per tweet)")
        parser.add_option('--index_file', dest='index_file',
                          default="index",
                          help="index file (must be able to write to this file)")
        parser.add_option('--lat', dest='lat',
                          help="The latitude for tweets")
        parser.add_option('--long', dest='long',
                          help="The longitude for tweets")
        parser.add_option('--place_id', dest='place_id',
                          help="Twitter ID of location for tweets")
        parser.add_option('--bbox', dest='bbox',
                          type='string',
                          action='callback',
                          callback=_get_comma_separated_args,
                          help="Bounding box (swlat, swlon, nelat, nelon) "
                               "of random tweet location")
        parser.add_option('--prefix', dest='prefix',
                          help="string to add to the beginning of each post "
                               "(if you want a space, include a space)")
        parser.add_option('--suffix', dest='suffix',
                          help="string to add to the end of each post "
                               "(if you want a space, include a space)")
        (options, args) = parser.parse_args()

        try:
            bot = EverywordBot(options.consumer_key, options.consumer_secret,
                               options.access_token, options.token_secret,
                               options.source_file, options.index_file,
                               options.lat, options.long, options.place_id,
                               options.prefix, options.suffix, options.bbox)
            bot.post()
            print "Tweeted at %s" % time.ctime()
            #reset timepassed
            startTime = time.ctime()
        except Exception as e:
            print "Error: %s" % e
        
        

