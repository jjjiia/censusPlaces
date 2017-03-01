##    
##    
#    $ python everywordbot.py --consumer_key="o9b6vjM8hs0iTzQkSA8oMUN7Y" --consumer_secret="Sj7SdfPtknaIAN5d9yyJqaqp7RpmWqMiZeTfDrPHRxEfNbT0Ek" \
#          --access_token="3332909505-49Zu2S9P9ZAh09SFE3G93D653RSpDjqSseKTXEf" --token_secret="omCvhWovaxUttfAbtNn22XCQrYvlY4z7pGYllR5w4Nr68" \
#          --source_file="test/test_source.txt" --index_file="index.txt"

import tweepy
import os
import oauth2, time, urllib, urllib2, json
from functools import partial
import random
import pprint
import pylab
import csv
import math
import json
from math import radians, cos, sin, asin, sqrt
from shapely.geometry import *
from shapely.ops import cascaded_union
from operator import itemgetter
import time
ACCESS = "KKEYUQJJVHZGPCPIGNGTEIC6MI"
SECRET = "YALZWSPPZAXTGV5C7FSXUK1WLE9ZF0WACXZEUBI7ONW972V4NT3S6QARD9V12W41"
URL = "https://openpaths.cc/api/1" 

previousInfo = ""


def build_auth_header(url, method):    
    params = {                                            
        'oauth_version': "1.0",
        'oauth_nonce': oauth2.generate_nonce(),
        'oauth_timestamp': str(int(time.time())),
    }
    consumer = oauth2.Consumer(key=ACCESS, secret=SECRET)
    params['oauth_consumer_key'] = consumer.key 
    request = oauth2.Request(method=method, url=url, parameters=params)  
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    request.sign_request(signature_method, consumer, None)
    return request.to_header()

# GET data (last 24 hours)
def formatNumber(number):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US')
    formated = str(int(round(number*1.0/1000)))+"k"
    return formated
    return locale.format("%d", number, grouping=True)

def loopPolygons(point):
    with open("data/nyc_bg.geojson") as f:
        js =json.load(f)
        for i in range(len(js['features'])):
            feature = js['features'][i]
            uid = feature["properties"]["GEOID"]
            polygon = shape(feature['geometry'])
            if polygon.contains(point)==True:
                foundId  = True
               # print str(uid)
                previousLocationId = str(uid)
                uidData = getById(uid,"data/socialExplorer_data.json")
                print uidData
                return
                results = "none"
                return results
                #return "J is in an area with median income of $"+ income+", and "+whites+"% white residents."
      #  print str(point)
        return "point out of bounds"+str(point)
                
        
def getById(uid, file):
    with open(file) as a:
        js = json.load(a)
        return str(int(js[uid]))

def sameAsLastLocation(currentUid):
      r = open("record.csv","r")
      recordReader = csv.reader(r)
      rlist = r.readlines()
      
      lastRecord = rlist[-1]
      lastUid = lastRecord.split(",")[0]
      print "last line", lastRecord
      print "compare",lastUid, currentUid
      if lastUid == currentUid:
          return True
      else:
          w = open("record.csv","a")
          recordWriter = csv.writer(w)
          recordWriter.writerow([currentUid,time.time()])
          return False
    
def getLocation():
    now = time.time()
    params = {'start_time': now - 24*60*60, 'end_time': now}    # get the last 24 hours
    query = "%s?%s" % (URL, urllib.urlencode(params))
    try:
        request = urllib2.Request(query)

        request.headers = build_auth_header(URL, 'GET')

        connection = urllib2.urlopen(request)
        data = json.loads(''.join(connection.readlines()))
        newData = {}
        for i in data[-1].keys():
            newData[str(i)]=str(data[-1][i])

        lat =data[-1]["lat"]
        lng = data[-1]["lon"]
        point = Point(float(lng),float(lat))

        plat = data[-2]["lat"]
        plng =  data[-2]["lon"]
        ppoint = Point(float(plng),float(plat))
        
        currentPosition = loopPolygons(point)
        previousPosition = loopPolygons(ppoint)

        currentUid = currentPosition["uid"]
        previousUid = previousPosition["uid"]
        
    
        if sameAsLastLocation(currentUid) ==True:
            print "same as last location pair"
            return None
        if currentUid == previousUid:
            print "no movement"
            return None
        else:
            print currentUid, previousUid     
            currentPositionTimeStamp=data[-1]["t"]
            previousPositionTimeStamp = data[-2]["t"]
            timeSpanMinutes = round(currentPositionTimeStamp-previousPositionTimeStamp)*1.0/60
            previousPosition["timePassed"]=timeSpanMinutes
            return previousPosition
#        return newData["lon"]+","+newData["lat"]+","+newData["t"]
        #print(json.dumps(data, indent=4))
    except urllib2.HTTPError as e:
        print(e.read()) 

def compose(results):
    print results["data"]
    print "# to choose from", len(results["data"].keys())
    
    keys = results["data"].keys()
    print keys
    #.remove('timeStamp').remove('point').remove('uid')
    picked = random.sample(range(0, len(keys)), 4)
    print "picked", picked
    
    valuesSentence = ""
    for i in picked:
        print i, keys[i],results["data"][keys[i]], toSentence(keys[i])
        valuesSentence+=toSentence(keys[i]).replace("XXX",str(results["data"][keys[i]]))
    
    minutesPassed = int(results["timePassed"])
    sentence = "J spent the last "+formatTimePassed(minutesPassed)+"in an area where "
    sentence = sentence+valuesSentence
    sentence = sentence[:-2]+"."
    print len(sentence)
    print sentence
    return sentence

def formatTimePassed(timePassed):
    if timePassed>=60:
        return str(int(float(timePassed)/60)) +" hrs "
    else:
        return str(timePassed)+" mins "
        
    
def toSentence(key):
    sentenceKey = {
        "business":"XXX% majored in business, ",
        "walk":"XXX% walk to work, ",
        "educator":"XXX% studied education, ",
        "drive":"XXX% drive to work, ",
        "publicTransportation":"XXX% use public transportation, ",
        "unemployeed":"XXX% are unemployeed, ",
        "income":"median income is $XXX, ",
        "leaveBefore5":"XXX% leave for work before 5am, ",
        "whites":"XXX% are white, "
    }
    return sentenceKey[key]

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
        #status_str = self._get_current_line(index)
        
        statusDictionary = getLocation()
        
        composed = compose(statusDictionary)
        #print composed
        
        statusString = composed
#        "J is at a place with median income of $"+str(statusDictionary["income"])+", where "+str(statusDictionary["whites"])+"% of residents are white, "+str(statusDictionary["unemployeed"])+"% are unemployeed, and "+str(statusDictionary["educator"])+"% majored in education."
#        +" and "
#        +str(statusDictionary["whites"])
#        +"% of white residents."
#        +str(statusDictionary["timeStamp"])
#        
        print "status", statusString
        status_str = statusString
        #status_str = "testing"
           # PreviousLocation = newData["lon"]+","+newData["lat"]+","+newData["t"]
        
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


def _csv_to_float_list(csv):
    return list(map(float, csv.split(',')))

for i in range(10000):
    print i
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
        time.sleep(20*60)
        