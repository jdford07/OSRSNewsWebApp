#fastAPI here
from fastapi import FastAPI
import mongoDBRequests
import osrsNewsCore

app = FastAPI()

@app.get("/")
def root():
    return {"Hello":"World"}

@app.get("/api/v1/MainNewsArticles")
def mainArticles():
    return osrsNewsCore.getOSRSMainPageNewsArticles()