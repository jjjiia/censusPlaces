#censusPlaces
import os
import oauth2, time, urllib, urllib2, json
from functools import partial
import random
import pprint
import csv
import math
import json
from math import radians, cos, sin, asin, sqrt
import sys
sys.path.append('/mas/u/zhangjia/.local/lib/python2.7/site-package')

from shapely.geometry import *
from shapely.ops import cascaded_union
from operator import itemgetter
import time
from collections import deque
import datetime
import pytz
ACCESS = "KKEYUQJJVHZGPCPIGNGTEIC6MI"
SECRET = "YALZWSPPZAXTGV5C7FSXUK1WLE9ZF0WACXZEUBI7ONW972V4NT3S6QARD9V12W41"
URL = "https://openpaths.cc/api/1" 

#api and data cleaning
#get existing api data from file openpaths_jjjiia.csv
#get new api data
#match date to add new data to end of old
#add bgid to new data part

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

def loopPolygons(point):
    with open("data/ny_ma.geojson") as f:
        js =json.load(f)
        for i in range(len(js['features'])):
            feature = js['features'][i]
            uid = feature["properties"]["GEOID"]
            polygon = shape(feature['geometry'])
            if polygon.contains(point)==True:
                return uid
                
def getLocation():
    now = time.time()
    params = {'start_time': now - 9*24*60*60, 'end_time': now}    # get the last 24 hours
    query = "%s?%s" % (URL, urllib.urlencode(params))
    try:
        request = urllib2.Request(query)

        request.headers = build_auth_header(URL, 'GET')

        connection = urllib2.urlopen(request)
        data = json.loads(''.join(connection.readlines()))
       # print data
        return data
    except urllib2.HTTPError as e:
        print(e.read())
#2017-02-21 14:56:00
        
def addIds():
    oldPoints = open("data/openpaths_jjjiia_withgid.csv","r")
    next(oldPoints)
    pointReader = csv.reader(oldPoints)
    
    withId =open(data/openpaths_jjjiia_i)
    for row in pointReader:
        print row
        point = Point(float(row[1]),float(row[0]))
        print point
        bgid = loopPolygons(point)
        print bgid
    
def getLastTimeOfOldData():
    oldPoints = open("data/openpaths_jjjiia_withgid.csv","r")
    pointReader = csv.reader(oldPoints)
    end = deque(pointReader,1)[0]
    endTime = end[3]
    return endTime
        
def findNewData():
    lastTime = getLastTimeOfOldData()
    print lastTime
    headers =["lat","lon","alt","t","device","os","version"]
    points = open("data/openpaths_jjjiia_withgid.csv","ab")
    pointsWriter = csv.writer(points,delimiter=',', lineterminator='\n')
    new = False
    #est = pytz.timezone('America/New_York')
    requestResults = getLocation()
    for i in requestResults:
       # print datetime.datetime.fromtimestamp(int(i["t"]),est)
        newTime = str(datetime.datetime.utcfromtimestamp(int(i["t"])))         
        if new == True:
            point = Point(float(i["lon"]),float(i["lat"]))
            bgid = str(loopPolygons(point))
            newDataRow = [i["lat"],i["lon"],i["alt"],newTime,i["device"],i["os"],i["version"],bgid]
            pointsWriter.writerow(newDataRow)
            print newDataRow
        if str(lastTime) == str(newTime):
            print lastTime,newTime
            new = True

            
        
def main():
    print "main"
#    addIds()
    findNewData()
    
for i in range(24*60/10*10000):
    try:
        main()
        print "running main", i
    except Exception as e:
        print "Error: %s" % e
    time.sleep(10*60)
    