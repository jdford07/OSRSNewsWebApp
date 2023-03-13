#fastAPI here
from fastapi import FastAPI
from dataclasses import dataclass
import mongoDBRequests
import osrsNewsCore

app = FastAPI()

@dataclass
class osrsNewsArticle:
    """DataClass that defines all notable elements of an OSRS News Article"""
    articleTitle: str
    articleType: str
    articleDate: str
    articleBody: str
    articleLink: str
    thumbnailUrl: str
    articleClass: str # String of either "mainPage or archive"
    month: int
    year: int
    
    
@app.get("/")
def root():
    return {"Hello":"World"}

@app.get("/api/v1/MainNewsArticles")
def getOSRSMainArticles():
    """Function to query the OSRSMainNewsArticles MongoDB collection for all 5 live OSRS Main Page articles
    Each article is converted to an osrsNewsArticle object for easy json return
    The list of objects are sorted by date in reverse fashion, to show the most recent article first, then returned"""
    mainArticleList = []
    
    mainArticles = mongoDBRequests.readOSRSNewsMainPageArticles("Consolidate", "OSRSMainNewsArticles") 
    
    for article in mainArticles:
        print(article['articleTitle'])
        mainArticleList.append(osrsNewsArticle(article['articleTitle'], article['articleType'], article['articleDate'], 
                                               article['articleBody'], article['articleLink'], article['thumbnailUrl'], 
                                               article['articleClass'], article['month'], article['year']))
    
    mainArticleList.sort(key=lambda element: element.articleDate, reverse=True)
    return mainArticleList
