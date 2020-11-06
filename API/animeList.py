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
animeListAll = []
listAll = []
statusTypes = []

class animeList(object):



    def updateAniListAnimeList():
        '''gets animeList from API and updates the anime list'''
        
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes
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
                                mediaListEntry {
                                    status
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

        


        #initializes variables
        aniListLength = len(animeListData['MediaListCollection']['lists']) #amount of lists user has
        statusTypes = []
        animeListPTW = []
        animeListCompleted = []
        animeListDropped = []
        animeListPaused = []
        animeListRepeating = []
        animeListCurrent = []
        statusTypes = []
            
        for x in range(0, aniListLength): #x is index of array

            status = animeListData['MediaListCollection']['lists'][x]['status']    #gets status from the list
            info = animeListData['MediaListCollection']['lists'][x]
            statusTypes.append(status)

            if(status == "PLANNING"):
                animeListPTW = animeListData['MediaListCollection']['lists'][x]
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

            

        

        #sorts all the lists in alphabetical order
        Sort.qSort(animeListPTW)
        Sort.qSort(animeListCompleted)
        Sort.qSort(animeListDropped)
        Sort.qSort(animeListPaused)
        Sort.qSort(animeListRepeating)
        Sort.qSort(animeListCurrent)

        listAll = [animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent]
        animeList.setAnimeListAll()
        Sort.qSort(animeListAll)

 
        pass

    def updateFiles():
        '''opens all the files and move them to the correct folder'''

        global animeListAll, statusTypes, listAll

        iterator = 0
        for status in statusTypes: #iterates through different statuses

            Path = getPath(status)
            files = os.listdir(Path)
            listAll[iterator]

            for aniFileName in files: #gets name of each file

                aniFileDir = Path + aniFileName

                with open(aniFileDir, "r+") as json_file: #opens each files and reads them
                    aniFile = json.load(json_file)
                    animeName = aniFile['Info']['Anime Name']
                    aniLoc = Search.bSearchAnimeList(animeListAll, animeName.title()) #gets the index of the anime in the animeList
                    aniFileStatus = aniFile['Info']['Status']
                    aniListStatus = animeListAll['entries'][aniLoc]['media']['mediaListEntry']['status']


                if(aniFileStatus != aniListStatus):

                    aniFile['Info']['Status'] = aniListStatus #changes status listed in file

                    fileName = numManip.makeSafe(animeName)

                    oPath = aniFileDir
                    nPath = getPath(aniListStatus) + fileName + ".txt"

                    os.rename(oPath, nPath) #moves file to correct directory

                    with open(nPath, "w+") as json_file:
                        json.dump(aniFile, json_file, indent = 4, ensure_ascii = True)

                        
            iterator += 1
        

    def setAnimeListAll():
        '''adds the entries of all the lists to animeListAll'''
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, listAll
        
        listAll = [animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent]


        animeListAll = []
        animeListAll = {
            'status' : 'ALL',
            'entries' : [],
            }


        for x in range(0, len(listAll) - 1): #iterates through the amount of lists
            
            if(len(listAll[x]) == 0): #moves to the next list if list does not exist
                listAll.pop(x)
            
            aniListLen = len(listAll[x]['entries'])

            for y in range(0, aniListLen): #iterates through entries in the list, adding them to the all list
                animeEntry = listAll[x]['entries'][y]
                animeListAll['entries'].append(animeEntry)

        pass


    def getAniId(animeId, status):
        '''changes the status of an anime on the API'''

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

        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll

        #sets correct list based on status
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
        elif(status == "ALL"):
            return animeListAll

        pass

    def getTitleList(status):
        '''returns a list containing only the names of the anime'''
        
        #gets correct list
        animeListStat = []
        animeListStat = animeList.getAnimeList(status)['entries']

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



