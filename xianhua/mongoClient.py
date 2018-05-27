#-*- coding: UTF-8 -*-   
#!/usr/bin/python
import pymongo
import json
from pymongo import MongoClient

def defaultMongoCient():
    client = MongoClient('127.0.0.1', 27017)
    return client

def localMongoClient():
    client = MongoClient('192.168.2.251', 27017)
    return client