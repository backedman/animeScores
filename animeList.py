import pathlib
import requests
import json
import webbrowser
from AniListAccess import *

animeListWatching = []
animeListPTW = []
animeListFinished = []


class animeList(object):

    #gets animeList from API
    def updateAniListAnimeList(status):
        global animeListWatching, animeListPTW, animeListFinished
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
        print(animeListData)

        #creates empty animeLists        
        animeListWatching = []
        animeListPTW = []
        animeListFinished = []

        #creats variables to use for loop
        totalPages = animeListData["data"]["Page"]["pageInfo"]["lastPage"]
        print(totalPages)
        index  = 0

        
        for page in range(2, totalPages):
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
                index  += 1
            
            #resets index for next iteration of loop
            index = 0

            #gets next page of results from query from website
            variables['page'] = page

            animeListDataRequest = AniListAccess.getData(query, variables)
            print(animeListDataRequest.headers["X-RateLimit-Remaining"])

            #compiles data
            animeListData = json.loads(animeListDataRequest.content)
            
        #print(animeListPTW)
       
    pass
    
    
    
    
    
    
    
    
    
    pass




