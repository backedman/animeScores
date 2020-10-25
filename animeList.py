import pathlib
import requests
import json
import webbrowser
from AniListAccess import *

animeListWatching = []
animeListPTW = []
animeListFinished = []
animeListAll = []


class animeList(object):

    #gets animeList from API
    def updateAniListAnimeList(status):
        global animeListWatching, animeListPTW, animeListFinished, animeListAll
        UserID = AniListAccess.getUserID()

        #sets query to send to server. This one asks for total number of pages, total anime, name of the anime in a page, and what list the anime is in
        query = '''
        query ($userID: Int, $status : MediaListStatus, $page : Int)  {
            Page(page : $page){
                pageInfo {                    
                    lastPage
                }
            
                mediaList(userId : $userID,  type: ANIME, status: $status) {
                    status
  	                media {
  	                    title{
                            romaji
                        }
                        tags{
                            name
                        }
                        duration
  	                }
                 }
              }
        }
        '''
        
        #sets correct information for the query. If all anime in the list are wanted, then status is not set

        if status == "all":
           variables = {
           'userID' : UserID,
           'page' : 1
           }

        else:
           variables = {
           'userID' : UserID,
           'status' : status,
           'page' : 1
           }

        
        animeListDataRequest = AniListAccess.getData(query, variables)
    
        #compiles the List Data
        animeListData = json.loads(animeListDataRequest.content)

        #creates empty animeLists        
        animeListWatching = []
        animeListPTW = []
        animeListFinished = []
        animeListAll = []

        #creats variables to use for loop
        totalPages = animeListData["data"]["Page"]["pageInfo"]["lastPage"]
        print(totalPages)
        index  = 0

        #iterates through each page (each page contains 50 anime which is the max amount that can be pulled from the API at once)
        for page in range(2, totalPages + 2):
            #adds each anime to corresponding list based on status
            for x in animeListData["data"]["Page"]["mediaList"]:
                animeStatus = animeListData["data"]["Page"]["mediaList"][index]["status"]
                animeInfo = animeListData["data"]["Page"]["mediaList"][index]["media"]

                if(animeStatus == "PLANNING"):
                    animeListPTW.append(animeInfo)
                    

                elif(animeStatus == "CURRENT"):
                    animeListWatching.append(animeInfo)

                elif(animeStatus == "COMPLETED"):
                    animeListFinished.append(animeInfo)
                
                #adds anime to the big list with every anime
                if(status == "all"):
                    animeListAll.append(animeInfo)
                index  += 1
            
            #resets index for next iteration of loop
            index = 0

            #gets next page of results from query from website
            variables['page'] = page

            animeListDataRequest = AniListAccess.getData(query, variables)
            print(animeListDataRequest.headers["X-RateLimit-Remaining"])

            #compiles data
            animeListData = json.loads(animeListDataRequest.content)
            
       
        pass
    
    #returns anime list with all information based on status
    def getAnimeList(status):

        #sets correct list based on status
        animeListStat = []
        if (status == "all"):
            animeListStat = animeListAll
        elif status == "PLANNING":
            animeListStat = animeListPTW
        elif status == "CURRENT":
            animeListStat = animeListWatching
        elif status == "COMPLETED":
            animeListStat = animeListFinished
        

        return animeListStat

        pass
    #returns a list containing only the names of the anime

    def getTitleList(status):
        
        #gets correct list
        animeListStat = []
        animeListStat = animeList.getAnimeList(status)

        #sets variables for loop
        titleList = []
        index = 0

        #adds names of anime to title list
        for x in animeListStat:
            animeTitle = animeListStat[index]["title"]["romaji"]
            titleList.append(animeTitle)
            index += 1
        
        return titleList    
        
    
    
        pass




