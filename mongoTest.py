from dotenv import load_dotenv, find_dotenv
import os
import pprint
from pymongo import MongoClient
from bson.objectid import ObjectId
load_dotenv(find_dotenv()) # Automatically find and load .env file

# MongoDB Cluster connection definition for "Personal" cluster
mongoDB_Personal_UserName = os.environ.get("MONGODB_USER")
mongoDB_Personal_Password = os.environ.get("MONGODB_PWD")
mongodb_Personal_ConnectionString = f"mongodb+srv://{mongoDB_Personal_UserName}:{mongoDB_Personal_Password}@personal.31iindg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongodb_Personal_ConnectionString)


# Function to insert a single record into a given Database's Collection
def insertSingleRecord(databaseName, collectionName, document):
    collection = client[databaseName][collectionName]

    try:
        recordID = collection.insert_one(document).inserted_id
        print(f"Successfully inserted [{recordID}] to [{databaseName}:{collectionName}]")
    except:
        print(f"Error inserting [{recordID}] to [{databaseName}:{collectionName}]")
    
    
# Function to delete a single record from a given Database's Collection
def deleteSingleRecord(databaseName, collectionName, documentID):
    collection = client[databaseName][collectionName]

    try:
        collection.delete_one({"_id": ObjectId(documentID)})
        print(f"Successfully deleted [{documentID}] from [{databaseName}:{collectionName}]") 
    except:
        print(f"Error deleting [{documentID}] from [{databaseName}:{collectionName}]")
    
    
# Function to specifically query the database for any OSRSNewsArticles with the articleClass = "mainPage"
def findOSRSNewsMainPageArticles(databaseName, collectionName):
    collection = client[databaseName][collectionName]
    returnArticles = []
    
    mainPageArticles = collection.find({"articleClass":"mainPage"})
    
    for article in mainPageArticles:
        returnArticles.append(article)
    
    return returnArticles

def findOSRSSpecificMonthArticles(databaseName, collectionName, currentMonth, currentYear):
    collection = client[databaseName][collectionName]
    returnArticles = []
    
    currentMonthArticles = collection.find({"$and":[
        {"month":currentMonth},
        {"year": currentYear}
    ]})
    
    for article in currentMonthArticles:
        returnArticles.append(article)
    
    return returnArticles
    

#findOSRSNewsMainPageArticles("Consolidate", "OSRSNewsArticles")