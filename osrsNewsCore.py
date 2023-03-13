# The core of this application has functions that are meant to be called upon by various cron jobs and not publicly accessible via the public facing FastAPI due to database updates

# Cron Job 1: Every 6 Hours call scrapeOSRSMainPageNewsArticles() to retreive a current list of the news articles posted to the oldschool.runescape.com website's MAIN PAGE then update the Atlas MongoDB 'OSRSMainNewsArticles' table accordingly

# Cron Job 2: Every 6 hours call get OSRSCurrentMonthArticles() to retreive a current list of the news articles posted to the oldschool.runescape.com website NEWS ARCHIVE then update the Atlas Mongo DB 'OSRSArchivedNewsArticles' table accordingly

import requests
from bs4 import BeautifulSoup
from datetime import *
from multiprocessing import *
from pprint import pprint
import mongoDBRequests
import json
import time
from dataclasses import dataclass

# DataClass that defines all notable elements of an OSRS News Article
@dataclass
class osrsNewsArticle:
    articleTitle: str
    articleType: str
    articleDate: str
    articleBody: str
    articleLink: str
    thumbnailUrl: str
    articleClass: str # String of either "mainPage or archive"
    month: int
    year: int


# Function to send a web request to grab all posted news articles on the OSRS Main Page then format the results into useable objects placed into a  List
def scrapeOSRSMainPageNewsArticles():
    osrsMainNewsArticlesList = []
    
    # Send the web request for a specific month & year page
    webUrl = f"https://oldschool.runescape.com/"
    webPageResult = requests.get(webUrl)
    
    # Beautiful Soup the HTML web request result and specify HTML section to dissect
    webPageSoupParsed = BeautifulSoup(webPageResult.content, "html.parser")
    soupNewsSection = webPageSoupParsed.find("section", class_="content")
    if(soupNewsSection != None):
        articleElements = soupNewsSection.find_all("article", class_="news-article")
    else:
        print(f"No Main Page News Articles Found")
        return
    
     # For each news article, grab relevant elements, create an object of relevant elements then place object into global list containing all news post objects
    for article in articleElements:
        # Find all relevant elements 
        titleElement = article.find("h3", class_="news-article__title")
        typeElement = article.find("span", class_="news-article__sub")
        dateElement = article.find("time", class_="news-article__time")
        bodyElement = article.find("p", class_="news-article__summary")
        linkElement = article.find("a", class_="news-article__figure-link")["href"]
        thumbnailLinkElement = article.find("img", class_="news-article__figure-img")["src"]
        
        # Convert Date String to DateTime Object to extract month/year of article post date
        dateStr = dateElement.text
        dateObj = datetime.strptime(dateStr, '%d %B %Y').date()
        month = dateObj.month
        year = dateObj.year
        
        # Create object of relevant elements
        articleObj = osrsNewsArticle(titleElement.text, typeElement.text, dateElement.text, bodyElement.text, linkElement, thumbnailLinkElement, "mainPage", month, year)
        
        # Append object to global list of all published news posts
        osrsMainNewsArticlesList.append(articleObj)
        
    syncOSRSMainPageArticles(osrsMainNewsArticlesList)
        
    return osrsMainNewsArticlesList

# Function to drop any existing "mainPage" articles from Consolidate:OSRSNewsArticles mongoDB collection that are not present in the "live" results gathered from the scrapeOSRSMainPageNewsArticles function
def syncOSRSMainPageArticles(articleList):
    storedArticles = mongoDBRequests.readOSRSNewsMainPageArticles("Consolidate", "OSRSMainNewsArticles") 
    
    # Check if any live articles need to be inserted (i.e. Not one of the stored articles)
    for liveArticle in articleList:
        insertFlag = True
        for storedArticle in storedArticles:
            if(liveArticle.articleTitle == storedArticle['articleTitle']):
                insertFlag = False
                print(f"{liveArticle.articleTitle} is already in [Consolidate:OSRSMainNewsArticles]")
                break
        if(insertFlag):
            print(f"Inserting {liveArticle.articleTitle}")
            mongoDBRequests.insertSingleRecord("Consolidate", "OSRSMainNewsArticles", liveArticle.__dict__)
    
    # Check if any stored articles need to be dropped (i.e Not one of the most recent live articles)
    for storedArticle in storedArticles:
        dropFlag = True
        for liveArticle in articleList:
            if(storedArticle['articleTitle'] == liveArticle.articleTitle):
                dropFlag = False
                print(f"{storedArticle['articleTitle']} is a live article")
                break
        if(dropFlag):
            print(f"{storedArticle['articleTitle']} is stale. Dropping {storedArticle['articleTitle']}")       
            mongoDBRequests.deleteSingleRecord("Consolidate", "OSRSMainNewsArticles", storedArticle['_id'])


# Function to send a web request to grab all posted news articles on a specified Month/Year then format the results into useable objects placed into a List. Pageination is supported for up to 2 pages for any Month/Year that has more than 1 news page
def scrapeOSRSArchivedNewsArticles(monthNumber, yearNumber, pageNumber = 1):
    osrsArchivedNewsArticlesList = []
    
    # Send the web request for a specific month & year page
    webUrl = f"https://secure.runescape.com/m=news/archive?oldschool=1&cat=0&year={yearNumber}&month={monthNumber}&page={pageNumber}"
   
    webPageResult = requests.get(webUrl)
    
    # Beautiful Soup the HTML web request result and specify HTML section to dissect
    webPageSoupParsed = BeautifulSoup(webPageResult.content, "html.parser")
    soupNewsSection = webPageSoupParsed.find("section", class_="content")
    if(soupNewsSection != None):
        articleElements = soupNewsSection.find_all("article", class_="news-list-article")
    else:
        print(f"No Archived News Articles Found for [{monthNumber}/{yearNumber}]")
        return
    
    # For each news article, grab relevant elements, create an object of relevant elements then place object into global list containing all news post objects
    for article in articleElements:
        # Find all relevant elements 
        titleElement = article.find("h4", class_="news-list-article__title")
        typeElement = article.find("span", class_="news-list-article__category")
        dateElement = article.find("time", class_="news-list-article__date")
        bodyElement = article.find("p", class_="news-list-article__summary")
        linkElement = article.find("a", class_="news-list-article__title-link")["href"]
        thumbnailLinkElement = article.find("img", class_="news-list-article__figure-img")["src"]
        
        # Convert Date String to DateTime Object to extract month/year of article post date
        dateStr = dateElement.text
        dateObj = datetime.strptime(dateStr, '%d %B %Y').date()
        month = dateObj.month
        year = dateObj.year
        
        # Create object of relevant elements
        articleObj = osrsNewsArticle(titleElement.text, typeElement.text, dateElement.text, bodyElement.text, linkElement, thumbnailLinkElement, "archived", month, year)
        
        # Append object to global list of all published news posts
        osrsArchivedNewsArticlesList.append(articleObj)
    
    paginationElement = soupNewsSection.find("a", class_="news-archive-next")
    if((paginationElement != None ) and (paginationElement.text == "Next")):
        paginatedArticles = scrapeOSRSArchivedNewsArticles(yearNumber, monthNumber, pageNumber+1)
        for article in paginatedArticles:
            osrsArchivedNewsArticlesList.append(article)
    
    return osrsArchivedNewsArticlesList
    
    
# Function to scrape the OSRS News website for any newly posted OSRS news articles for the current month then insert any new articles in the Consolidate OSRSArchivedNewsArticles mongoDB
def scrapeOSRSCurrentMonthArticles(currentMonth, currentYear):
    
    newestOSRSArticles = scrapeOSRSArchivedNewsArticles(currentMonth, currentYear)
    osrsCurrentMonthArticles = mongoDBRequests.readOSRSSpecificMonthArticles("Consolidate", "OSRSArchivedNewsArticles", currentMonth, currentYear) 
    
    for liveArticle in newestOSRSArticles:
        if(any(article['articleTitle'] == liveArticle.articleTitle for article in osrsCurrentMonthArticles)):
            print(f"{liveArticle.articleTitle} already exists in [Consolidate:OSRSArchivedNewsArticles]")
        else:
            print(f"Inserting {liveArticle.articleTitle} in [Consolidate:OSRSArchivedNewsArticles]")
            mongoDBRequests.insertSingleRecord("Consolidate", "OSRSArchivedNewsArticles", liveArticle.__dict__)
   
            
# Function to query the OSRSMainNewsArticles MongoDB collection for all 5 live articles
def getOSRSMainPageArticles():
    mainArticles = mongoDBRequests.readOSRSNewsMainPageArticles("Consolidate", "OSRSMainNewsArticles") 
    return mainArticles

# Function to query the OSRSArchivedNewsArticles MongoDB collection for all OSRS news articles for the current month
def getOSRSCurrentMonthArticles(currentMonth, currentYear):
    currentMonthArticles = mongoDBRequests.readOSRSSpecificMonthArticles("Consolidate", "OSRSArchivedNewsArticles", currentMonth, currentYear) 
    return currentMonthArticles
    
# Global declarations (declared in each process)
today = date.today()
currentYear = date.today().year
currentMonth = date.today().month

# Grab all news articles from the OSRS website published from the past 2 years
if __name__ == '__main__':
    print("Grabbing main page articles...")
    scrapeOSRSMainPageNewsArticles()
    # scrapeOSRSCurrentMonthArticles(currentMonth, currentYear)
    # print("================= GET MAIN PAGE ARTICLES =================")
    # print(getOSRSMainPageArticles())
    # print("================= GET CURRENT MONTH ARTICLES =================")
    # print(getOSRSCurrentMonthArticles(currentMonth, currentYear))
    