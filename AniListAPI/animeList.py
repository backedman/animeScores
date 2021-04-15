import pathlib
import requests
import json
import webbrowser
import time
import operator
#from main import addSpacing
from AniListAPI.AniListAccess import *
from runnables.config import *
from Algorithms.Sort import *
from Algorithms.Search import *
from Algorithms.valManip import *


animeListPTW = []
animeListCompleted = []
animeListDropped = []
animeListPaused = []
animeListRepeating = []
animeListCurrent = []
animeListAll = []
animeListDet = []
listAll = []
statusTypes = []
genreTags = []

class animeList():



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
                                    score
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

        animeList.setAnimeListAll() #adds all the other lists into one big list
        Sort.qSort(animeListAll)

 
        pass

    def updateAnimeListDet(user):
        '''gets animeLists from API'''
        
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes
        if(user == ""):
            print("here")
            userName = AniListAccess.getUserName()
        else:
            userName = user

        print(userName)

        #sets query to send to server. This one asks for total number of pages, total anime, name of the anime in a page, and what list the anime is in
        query = '''
        query ($userName: String)  {
                MediaListCollection(userName : $userName,  type: ANIME) {
                    
                     lists {
                          
                          status

                          entries {

                            mediaId
                            media {
                              title{
                                userPreferred
                              }

                              genres

                              tags{
                                name
                                rank
                                category
                              }

                              averageScore
                              popularity

                              mediaListEntry {
                                    score
                                }

                            }

                          }
    }
                }
        }
        '''
        
        #sets correct information for the query. If all anime in the list are wanted, then status is not set
        variables = {
            'userName' : userName,
        }

        #requests data from API into a list 
        animeListData = AniListAccess.getData(query, variables)['data']['MediaListCollection']['lists']

        if(user == "" or user == AniListAccess.getUserName()):
            animeListDet = animeListData

        return animeListData

    def updateFiles():
        '''opens all the files and move them to the correct folder'''

        global animeListAll, statusTypes, listAll

        iterator = 0
        for status in statusTypes: #iterates through different statuses

            Path = valManip.getPath(status)
            files = os.listdir(Path)
            listAll[iterator]


            for aniFileName in files: #gets name of each file

                aniFileDir = Path + aniFileName

                with open(aniFileDir, "r+") as json_file: #opens each files and reads them
                    aniFile = json.load(json_file)
                    animeName = aniFile['Info']['Anime Name']
                    aniLoc = Search.bSearchAnimeList(animeListAll, animeName.title()) #gets the index of the anime in the animeList

                    try:
                        aniListStatus = animeListAll['entries'][aniLoc]['media']['mediaListEntry']['status']

                    except TypeError: #if the anime from file cannot be found in the data brought in from the api, it throws an error message to check for later
                        print("ERROR COULD NOT FIND " + animeName)

                if(status != aniListStatus):

                    aniFile['Info']['Status'] = aniListStatus #changes status listed in file

                    fileName = valManip.makeSafe(animeName)

                    oPath = aniFileDir
                    nPath = valManip.getPath(aniListStatus) + fileName + ".txt"

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


        for x in range(0, len(listAll)): #iterates through the amount of lists (PTW, Completed, Dropped, etc.) 
            
            if(len(listAll[x]) == 0): #moves to the next list if list does not exist (user has no anime in that list)
                listAll.pop(x)
            
            aniListLen = len(listAll[x]['entries'])

            for y in range(0, aniListLen): #iterates through entries in the list, adding them to the all list
                animeEntry = listAll[x]['entries'][y]
                animeListAll['entries'].append(animeEntry)

        pass






    


        






#
#                                below are all the get methods
#
    
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
            print(animeListAll)
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
        '''returns an alphabetically sorted anime list'''
        return Sort.qSort(aniList)

    
    def getAnimeDetailed(animeName):
        '''gets detailed list of anime'''

        #sets query and variables to get anime from API
        query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    title{
                        userPreferred
                    }
                    tags{
                        name
                        rank
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

    def getAnimeListDet():
        global animeListDet

        if(animeListDet == []):
            return animeList.updateAnimeListDet("")
        else:
            return animeListDet

    def getAnimeSearch(animeName):
        '''gets first search result of anime search'''
        query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
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

    def getEntryId(animeName):
        '''gets list entry ID (required to change anything related to the anime on the website)'''
        global animeListAll

        aniLoc = Search.bSearchAnimeList(animeListAll, animeName.title()) #gets the index of the anime in the animeList

        entryId = animeListAll['entries'][aniLoc]['id'] #gets the entry ID of the specific anime in the list

        return entryId


    def getAnimeSearchList(animeName, numResults):
        '''gets multiple search results'''
        
        query = '''
            query ($animeName: String, $perPage: Int)  {
            Page(perPage : $perPage){
  	                media(search : $animeName, type : ANIME)
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

    def getAllGenreTags():
        '''returns all possible genres and tags available on anilist. Index 0 contains genres and Index 1 contains tags'''
        global genreTags

        query = '''
            {
                GenreCollection
                MediaTagCollection{
                    name
                }
            }
        '''

        variables = {
            }

        #returns anime results list
        animeData = (AniListAccess.getData(query,variables)['data'])

        #splits tags and genres into seperate lists
        genre = animeData['GenreCollection']
        tags = animeData['MediaTagCollection']

        #removes the 'name' portion in the list to make it identical to the genre list
        for x in range(0, len(tags)):
            tags[x] = tags[x]['name']                   

        genreTags = [genre, tags]

        return genreTags




