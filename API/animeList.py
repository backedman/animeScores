import pathlib
import requests
import json
import webbrowser
import time
from API.AniListAccess import *

animeListWatching = []
animeListPTW = []
animeListCompleted = []
animeListAll = []


class animeList(object):

    def updateAniListAnimeList(status):
        '''gets animeList from API and updates the anime list'''
        
        global animeListWatching, animeListPTW, animeListCompleted, animeListAll
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
  	                }
                 }
              }
        }
        '''
        
        #sets correct information for the query. If all anime in the list are wanted, then status is not set
        dur = 0
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
 
        #requests data from API        
        animeListDataRequest = AniListAccess.getData(query, variables)

        #compiles the List Data
        animeListData = json.loads(animeListDataRequest.content)

        #creates empty animeLists based on status
        if(status == "all"):
            animeListWatching.clear()
            animeListPTW.clear()
            animeListCompleted.clear()
            animeListAll.clear()
        elif(status == "PLANNING"):
            animeListPTW.clear()
        elif(status == "CURRENT"):
            animeListWatching.clear()
        elif(status == "COMPLETED"):
            animeListCompleted.clear()
        
        #creats variables to use for loop
        totalPages = animeListData["data"]["Page"]["pageInfo"]["lastPage"]
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
                    animeListCompleted.append(animeInfo)
                
                #adds anime to the big list with every anime if parameter is given
                if(status == "all"):
                    animeListAll.append(animeInfo)
                index  += 1
            
            #resets index for next iteration of loop
            index = 0

            #gets next page of results from query from website
            variables['page'] = page
            animeListDataRequest = AniListAccess.getData(query, variables)
                #prints out amount of times data can be pulled from website in the minute
            print(animeListDataRequest.headers["X-RateLimit-Remaining"])

            #compiles data
            animeListData = json.loads(animeListDataRequest.content)

        #returns anime list asked for
        return animeList.getAnimeList(status)
    
    def getAnimeList(status):
        '''returns anime list with all information based on status'''

        #sets correct list based on status
        animeListStat = []
        if (status == "all"):
            animeListStat = animeListAll
        elif status == "PLANNING":
            animeListStat = animeListPTW
        elif status == "CURRENT":
            animeListStat = animeListWatching
        elif status == "COMPLETED":
            animeListStat = animeListCompleted
        
        #updates list if the list is empty for some reason
        if(len(animeListStat) == 0):
            animeListStat = animeList.updateAniListAnimeList(status)

        return animeListStat

        pass

    def getTitleList(status):
        '''returns a list containing only the names of the anime'''
        
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

    #gets the episode info

    
    
    def getAnimeDetailed(animeName):
        """gets detailed list of anime"""

        #sets query and variables to get anime from API
        query = '''
            query($animeName : String) {
                Media(search : $animeName)
                {
                    title{
                        romaji
                    }
                    tags{
                        name
                    }
                    episodes
                    genres
                    duration
                    averageScore
                    meanScore
                    favourites
                }
            }
            '''
        variables = {
            'animeName' : animeName
        }

        #returns json data of anime
        animeData = (json.loads((AniListAccess.getData(query, variables)).content))['data']['Media']
        return animeData

    def getAnimeSearch(animeName):
        '''gets first search result of anime search'''
        query = '''
            query($animeName : String) {
                Media(search : $animeName)
                {
                    title{
                        romaji
                    }
                    episodes                  
                    duration
                }
            }
            '''
        variables = {
            'animeName' : animeName
        }
        
         #returns json data of anime
        animeData = (json.loads((AniListAccess.getData(query, variables)).content))['data']['Media']
        return animeData




