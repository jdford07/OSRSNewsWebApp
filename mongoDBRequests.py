from dotenv import load_dotenv, find_dotenv
import os
import pprint
import urllib.parse
from pymongo import MongoClient
from bson.objectid import ObjectId
load_dotenv(find_dotenv()) # Automatically find and load .env file

# MongoDB Cluster connection definition for "Personal" cluster
mongoDBPersonalUserNameRW = os.environ.get("MONGODB_USER")
mongoDBPersonalPasswordRW = urllib.parse.quote_plus(os.environ.get("MONGODB_PWD"))
mongodbPersonalConnectionStringRW = f"mongodb+srv://{mongoDBPersonalUserNameRW}:{mongoDBPersonalPasswordRW}@personal.31iindg.mongodb.net/?retryWrites=true&w=majority"
mongoDBPersonalUserNameR = os.environ.get("MONGODB_READ_USER")
mongoDBPersonalPasswordR = urllib.parse.quote_plus(os.environ.get("MONGODB_READ_PWD"))
mongodbPersonalConnectionStringR = f"mongodb+srv://{mongoDBPersonalUserNameR}:{mongoDBPersonalPasswordR}@personal.31iindg.mongodb.net/?retryWrites=true&w=majority"
clientReadWrite = MongoClient(mongodbPersonalConnectionStringRW)
clientRead = MongoClient(mongodbPersonalConnectionStringR)


# Function to insert a single record into a given Database's Collection
def insertSingleRecord(databaseName, collectionName, document):
    collection = clientReadWrite[databaseName][collectionName]

    try:
        recordID = collection.insert_one(document).inserted_id
        print(f"Successfully inserted [{recordID}] to [{databaseName}:{collectionName}]")
    except:
        print(f"Error inserting [{recordID}] to [{databaseName}:{collectionName}]")
    
    
# Function to delete a single record from a given Database's Collection
def deleteSingleRecord(databaseName, collectionName, documentID):
    collection = clientReadWrite[databaseName][collectionName]

    try:
        collection.delete_one({"_id": ObjectId(documentID)})
        print(f"Successfully deleted [{documentID}] from [{databaseName}:{collectionName}]") 
    except:
        print(f"Error deleting [{documentID}] from [{databaseName}:{collectionName}]")
    
    
# Function to specifically query the database for any OSRSNewsArticles with the articleClass = "mainPage"
def readOSRSNewsMainPageArticles(databaseName, collectionName):
    collection = clientRead[databaseName][collectionName]
    returnArticles = []
    
    mainPageArticles = collection.find({"articleClass":"mainPage"})
    
    for article in mainPageArticles:
        returnArticles.append(article)
    
    return returnArticles

def readOSRSSpecificMonthArticles(databaseName, collectionName, currentMonth, currentYear):
    collection = clientRead[databaseName][collectionName]
    returnArticles = []
    
    currentMonthArticles = collection.find({"$and":[
        {"month":currentMonth},
        {"year": currentYear}
    ]})
    
    for article in currentMonthArticles:
        returnArticles.append(article)
    
    return returnArticles
    