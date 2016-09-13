import requests
import json
from bs4 import BeautifulSoup

# ---------------- SETTINGS -------------------------
saveToJsFile = True
saveToJsonFile = True

urlToScrape = 'http://ufc.com/rankings'
archiveYearlyUrls = [ # just add one url from archive.org per year that you wanna scrape
    'http://web.archive.org/web/20130301000000*/',
    'http://web.archive.org/web/20140301000000*/',
    'http://web.archive.org/web/20150301000000*/',
    'http://web.archive.org/web/20160301000000*/'] 
    
# ---------------- MAIN -------------------------

snapshotUrls = []
def Main():
    for archiveUrl in archiveYearlyUrls:
        archiveUrl += urlToScrape;
        currentYearUrls = GetLinksFromInternetArchive(archiveUrl)
        
        #select unique months
        lastSelectedMonth = ''
        for link in currentYearUrls:
            month = link["month"] 
            if month != lastSelectedMonth:
                lastSelectedMonth = month
                snapshotUrls.append(link)

    rankingsData = GetRankings(snapshotUrls)

    if SaveToJavascriptFile:
        SaveToJsonFile("data.json", "data", rankingsData) 
    if saveToJsFile:
        SaveToJavascriptFile("data.js", "data", rankingsData, "window.historicalRankings = " )

# ---------------- HELPERS -------------------------

# Get property value from first html element in array
def GetPropertyValue(arr, prop):
    if (len(arr) > 0):
        return arr[0].get(prop)
    else:
        return ''; 

# Get inner text from first html element in array
def GetText(arr):
    if (len(arr) > 0):
        return arr[0].text.strip('\t\n\r')
    else:
        return ''; 

# create if not exists
def SaveToJsonFile(filename, jsonRootObjectName, jsonData):
    with open(filename, "w+") as file:
        print(file.readlines())
    with open(filename, "w+") as outfile:
        json.dump({jsonRootObjectName: jsonData}, outfile, indent=4)
    file.close()

    with open(filename) as file:
        result = json.load(file)
    file.close()
    return;

# save to a js file to be used by the frontend
def SaveToJavascriptFile(filename, jsonRootObjectName, jsonData, jsCode ):
    with open(filename, "w+") as outfile:
        outfile.write(jsCode);
        json.dump({jsonRootObjectName: jsonData}, outfile, indent=4)
    return;
    
def GetStartAndStopDateFromInternetArchive(url):
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser") 
    metaLinks = html.select(".wbMeta > a")
    archiveDateLinks = filter(lambda x: x["href"].startswith("/web/"), metaLinks)
    return archiveDateLinks

# ---------------- SCRAPER -------------------------

# Get snapshots from web.archive.org as array of URL:s
# example output: ['http://web.archive.org/web/20140107064816/http://www.ufc.com/rankings?id=']
def GetLinksFromInternetArchive(url):
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser") 

    results = []
    for day in html.select(".day > a"):
        snapshot = {}
        snapshot["url"] = 'http://web.archive.org' + day.get("href")
        date = day.get("class")
        snapshot["date"] = date
        snapshot["year"] = date[5]
        snapshot["month"] = date[1]
        results.append(snapshot)
    return results;

# ---------------- UFC DATA -------------------------

class Fighter(object):
    def __init__(self, name="Unknown name", url="", rank=-1):
        self.name = name
        self.url = url
        self.rank = rank

# Parse fighters
# from <TR> elements on ufc.com/rankings
def GetFighters(tableRows):
    fighters = []
    for row in tableRows:
        fighter = {}
        fighter["name"] = GetText(row.select(".name-column > a"))
        fighter["url"] = GetPropertyValue(row.select(".name-column > a"), "href")
        fighter["rank"] = GetText(row.select(".number-column"))
        fighters.append(fighter)
    return fighters;

# Scrape and parse fighters from ufc.com/rankings pages via internetarchive 
def GetRankings(snapshotUrls):
    returnData = []
    for snapshot in snapshotUrls:
        result = {}
        result["url"] = snapshot["url"]
        result["date"] = snapshot["date"]
        result["displayDate"] = snapshot["month"] + " " + snapshot["year"]
        url = result["url"]
        r = requests.get(url)
        html = BeautifulSoup(r.text, "html.parser") 
        divisions = html.select(".ranking-list")
        
        print str(len(divisions)) + " divisions were found"
        result["divisions"] = []
        for d in divisions:
            newDiv = {}
            newDiv["title"] = GetText(d.select("#weight-class-name"))
            if (newDiv["title"]  == ""):
                newDiv["title"]  = GetText(d.select(".weight-class-name"))
                
            newDiv["champ"] = GetText(d.select(".rankings-champions .fighter-name a"))
            newDiv["champUrl"] = GetText(d.select(".rankings-champions .fighter-name a"))
            champ = {}
            champ["name"] =  newDiv["champ"] 
            champ["url"] =  newDiv["champUrl"] 
            champ["rank"] =  "0"
            
            tableRows = d.select(".rankings-table tr")
            fighters = GetFighters(tableRows)
            fighters.insert(0, champ) #add the champ
            newDiv["fighters"] = fighters
            result["divisions"].append(newDiv)
            
            print newDiv["title"] + " champ " + result["displayDate"] + ":" +  newDiv["champ"]
        
        returnData.append(result)
            
        #print fighters
    return returnData


# ---------------- START -------------------------
Main()