import requests
import json
from bs4 import BeautifulSoup

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

# Save to to file, create if not exists
def SaveToJsonFile(data, filename, rootObjectName):
    with open(filename, "w+") as file:
        print(file.readlines())
    with open(filename, "w+") as outfile:
        json.dump({rootObjectName: data}, outfile, indent=4)
    file.close()

    with open(filename) as file:
        result = json.load(file)
    file.close()
    return;
    
    
def GetStartAndStopDateFromInternetArchive(url):
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser") 
    metaLinks = html.select(".wbMeta > a")
    archiveDateLinks = filter(lambda x: x["href"].startswith("/web/"), metaLinks)
    return archiveDateLinks

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
        result["displayDate"] = snapshot["month"] + "-" + snapshot["year"]
        url = result["url"]
        r = requests.get(url)
        html = BeautifulSoup(r.text, "html.parser") 
        divisions = html.select(".ranking-list")

        for d in divisions:
            divisionTitle = GetText(d.select("#weight-class-name"))
            divisionChampName = GetText(d.select(".rankings-champions .fighter-name a"))
            divisionChampUrl = GetText(d.select(".rankings-champions .fighter-name a"))
            
            tableRows = d.select(".rankings-table tr")
            fighters = GetFighters(tableRows)
            result["fighters"] = fighters
            returnData.append(result)
            
            print divisionTitle, divisionChampName
            print str(len(tableRows)) + " rankings were found"
            print fighters
    return returnData


# Main program
urlToScrape = 'http://ufc.com/rankings'
archiveYearlyUrls = [ # one url per year in web.archive.org
    'http://web.archive.org/web/20130301000000*/',
    'http://web.archive.org/web/20140301000000*/',
    'http://web.archive.org/web/20150301000000*/',
    'http://web.archive.org/web/20160301000000*/'] 
    
links = GetStartAndStopDateFromInternetArchive(urlToScrape)
print len(links)