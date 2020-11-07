import pathlib
import requests
import json
import webbrowser
import time
from API.AniListAccess import *
from runnables.main import *
from Algorithms.Search import *
from Algorithms.Sort import *


animeListPTW = []
animeListCompleted = []
animeListDropped = []
animeListPaused = []
animeListRepeating = []
animeListCurrent = []
statusTypes = []

class animeList(object):



    def updateAniListAnimeList():
        '''gets animeList from API and updates the anime list'''
        
        global animeListWatching, animeListPTW, animeListCompleted, animeListAll
        UserID = AniListAccess.getUserID()

        #sets query to send to server. This one asks for total number of pages, total anime, name of the anime in a page, and what list the anime is in
        query = '''
        query ($userID: Int)  {
                MediaListCollection(userId : $userID,  type: ANIME) {
                    
                    lists{
                        status
                        entries{
                            id
                            media {
                                id
  	                            title{
                                    userPreferred
                                }
  	                        }
                        }
                    }
                }
        }
        '''
        
        #sets correct information for the query. If all anime in the list are wanted, then status is not set
        variables = {
            'userID' : UserID,
        }


        #requests data from API into a list 
        animeListData = AniListAccess.getData(query, variables)['data']
        print(animeListData)

        


        #initializes variables
        aniListLength = len(animeListData['MediaListCollection']['lists']) #amount of lists user has
        print(str(aniListLength))
        statusTypes = []
        animeListPTW = []
        animeListCompleted = []
        animeListDropped = []
        animeListPaused = []
        animeListRepeating = []
        animeListCurrent = []
        animeListAll = []
        statusTypes = []
            
        for x in range(0, aniListLength): #x is index of array

            status = animeListData['MediaListCollection']['lists'][x]['status']    #gets status from the list
            print('here0')
            statusTypes.append(status)

            if(status == "PLANNING"):
                animeListPTW = animeListData['MediaListCollection']['lists'][x]
                print(animeListPTW)
            elif(status == "COMPLETED"):
                animeListCompleted = animeListData['MediaListCollection']['lists'][x]
            elif(status == "DROPPED"):
                animeListDropped = animeListData['MediaListCollection']['lists'][x]
            elif(status == "PAUSED"):
                animeListPaused = animeListData['MediaListCollection']['lists'][x]
            elif(status == "REPEATING"):
                animeListRepeating = animeListData['MediaListCollection']['lists'][x]
            elif(status == "CURRENT"):
                animeListCurrent = animeListData['MediaListCollection']['lists'][x]

            

        print("hereb")
        

        #sorts all the lists in alphabetical order
        print(animeListPTW)
        Sort.qSort(animeListPTW)
        print("ptw")
        Sort.qSort(animeListCompleted)
        print("Completed")
        Sort.qSort(animeListDropped)
        print("Dropped")
        Sort.qSort(animeListPaused)
        print("Paused")
        Sort.qSort(animeListRepeating)
        print("Repeating")
        Sort.qSort(animeListCurrent)
        print("Current")

        animeListAll += animeListPTW

        print(animeListAll)

 
        pass

    def updateFiles():
        '''opens all the files and move them to the correct folder'''

        
        for status in statusTypes: #iterates through different statuses
            print("here4")
            Path = getPath(status)
            print("here5")
            files = os.listdir(Path)
            print('here1')
            animeListAll = animeList.getAnimeList("all")

            for aniFileName in files: #gets name of each file

                aniFileDir = Path + aniFileName
                print('here2')

                with open(aniFileDir, "r+") as json_file: #opens each files and reads them
                    print(aniFileDir)
                    aniFile = json.load(json_file)
                    animeName = aniFile['Info']['Anime Name']
                    aniLoc = Search.bSearchAnimeList(animeListAll, animeName) #gets the index of the anime in the animeList
                    aniFileStatus = aniFile['Info']['Status']
                    aniListStatus = animeListAll[aniLoc]['status']

                    #if(aniFileStatus != aniListStatus):
                    aniFile['Info']['Status'] = aniListStatus
                    animeId = int(animeListAll[aniLoc]['media']['id'])
                    print(animeList.getAniId(animeId, status))
    

    def getAniId(animeId, status):
        '''changes the status of an anime on the API'''
        print('here3')

        query = '''
            mutation ($mediaId: Int) {
                SaveMediaListEntry (mediaId: $mediaId) {
                    id
                }
            }
        '''

        variables = {
            'mediaId' : animeId
            }

        animeListData = AniListAccess.getData(query, variables)
        listId = animeListData['data']['SaveMediaListEntry']['id']

        return listId
    
    def getAnimeList(status):
        '''returns anime list with all information based on status'''

        #sets correct list based on status
        animeListStat = []
        if(status == "PLANNING"):
            return animeListPTW
        elif(status == "COMPLETED"):
            return animeListCompleted
        elif(status == "DROPPED"):
            return animeListDropped
        elif(status == "PAUSED"):
            return animeListPaused
        elif(status == "REPEATING"):
            return animeListRepeating
        elif(status == "CURRENT"):
            return animeListCurrent


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
            animeTitle = animeListStat[index]['media']["title"]["userPreferred"]
            titleList.append(animeTitle)
            index += 1
        titleList.sort()
        return titleList    
        
    
    
        pass


    def getAnimeListSorted(aniList):
        return Sort.qSort(aniList)

    
    def getAnimeDetailed(animeName):
        """gets detailed list of anime"""

        #sets query and variables to get anime from API
        query = '''
            query($animeName : String) {
                Media(search : $animeName)
                {
                    title{
                        userPreferred
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
        animeData = (AniListAccess.getData(query, variables))['data']['Media']
        return animeData

    def getAnimeSearch(animeName):
        '''gets first search result of anime search'''
        query = '''
            query($animeName : String) {
                Media(search : $animeName)
                {
                    title{
                        userPreferred
                    }
                    episodes                  
                    duration
                }
            }
            '''
        variables = {
            'animeName' : animeName
        }
        
         #returns data of anime
        animeData = (AniListAccess.getData(query, variables))['data']['Media']
        return animeData

    def getAnimeSearchList(animeName, numResults):
        '''gets multiple search results'''
        
        query = '''
            query ($animeName: String, $perPage: Int)  {
            Page(perPage : $perPage){
  	                media(search : $animeName)
                    {
                        title{
                            userPreferred
                        }
                        episodes                  
                        duration
                    }
                }
            }
        '''
        variables = {
                'animeName' : animeName,
                'perPage' : numResults
            }

        #returns anime results list
        animeData = (AniListAccess.getData(query,variables))['data']['Page']
        return animeData



