import pathlib
from turtle import Terminator
import requests
import json
import webbrowser
import time
import operator
#from main import addSpacing
from AniListAPI.AniListAccess import *
from AniListAPI.AniListCalls import *
from runnables.config import *
from Algorithms.Sort import *
from Algorithms.Search import *
from Algorithms.valManip import *
from datetime import date


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

        #sets query to send to server.  This one asks for total number of
        #pages, total anime, name of the anime in a page, and what list the
        #anime is in
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
        
        #sets correct information for the query.  If all anime in the list are
        #wanted, then status is not set
        variables = {
            'userID' : UserID,
        }


        #requests data from API into a list
        animeListData = AniListAccess.getData(query, variables)['data']		


        #initializes variables
        aniListLength = len(animeListData['MediaListCollection']['lists']) #amount of lists user has
        statusTypes = []
        animeListPTW = dict()
        animeListCompleted = dict()
        animeListDropped = dict()
        animeListPaused = dict()
        animeListRepeating = dict()
        animeListCurrent = dict()
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
        #Sort.qSort(animeListPTW)
        #Sort.qSort(animeListCompleted)
        #Sort.qSort(animeListDropped)
        #Sort.qSort(animeListPaused)
        #Sort.qSort(animeListRepeating)
        #Sort.qSort(animeListCurrent)

        animeList.setAnimeListAll() #adds all the other lists into one big list
        Sort.qSort(animeListAll)

 
        pass

    def updateAnimeListDet(user="", sort="MEDIA_ID"):
        '''gets animeLists from API'''
        
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes, animeListDet
        if(user == ""):
            userName = AniListAccess.getUserName()
        else:
            userName = user

        if(sort is None):
            sort = "MEDIA_ID"

        #sets query to send to server.  This one asks for total number of
        #pages, total anime, name of the anime in a page, and what list the
        #anime is in
        query = '''
        query ($userName: String, $sortType: [MediaListSort])  {
                MediaListCollection(userName : $userName,  type: ANIME, sort: $sortType) {
                    
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

                              recommendations{
                                edges{
                                    node{
                                        rating
                                        mediaRecommendation{
                                            title{
                                                userPreferred
                                            }
                                        }
                                    }
                        }
                    }

                            }

                          }
            }
                }
        }
        '''
        
        #sets correct information for the query.  If all anime in the list are
        #wanted, then status is not set
        variables = {
            'userName' : userName,
            'sortType' : sort
        }

        #requests data from API into a list
        animeListData = AniListAccess.getData(query, variables)['data']['MediaListCollection']['lists']

        if(user == "" or user == AniListAccess.getUserName()):
            animeListDet = animeListData

        return animeListData


    def updateFullAnime(reaquire=False, animeListType=None, animeName=None, status=None):
        """updates the data/text file containing the information on all the anime. The function can replace all the information in the
           data function by pulling from the API again (if reaquire=True), update whatever anime is on our list (animeListType=(type)) based on given list status, or the status
           of an individual anime (given animeName and new status). Only one of these things can occur, with reaquire taking precedence over updating based on list status
           and updating by list status taking precedence over updating an individual anime


        Args:
            reaquire (bool, optional): whether or not we should pull all information from the api or not. Defaults to False.
            animeListType (string, optional): updates the values of the anime in the text file based on the anime in a specific list (ex. animeListType="COMPLETED" will update all the currently completed anime in the full list to actually be completed)
            animeName (string, optional): name of the anime that is being updated. Defaults to None.
            status (string, optional): the status the anime is being changed to. Defaults to None.
        """

        if(reaquire):
            pass

        elif(animeListType is not None):
            
            List = animeList.getAnimeList(animeListType)['entries']
            animeData = animeList.getAnimeList("FULL")

            if(animeList is None or animeData is None):
                return None

            #print(List)

            progress = 10
            print(str(int(progress)) + "% done", end="\r")
            slices = 80/len(List)

            for anime in List:

                anime = anime['media']

                print(str(int(progress)) + "% done", end="\r")
                progress += slices


                if(animeListType == "ALL"):
                    curr_status = anime['mediaListEntry']['status']
                    #print(curr_status)
                else:
                    curr_status = animeListType

                title = anime['title']['userPreferred']

                for anime2 in animeData:

                    title2 = anime2['title']['userPreferred']
                    

                    if(title.title() == title2.title()):
                        #print(title + " changed to " + curr_status)
                        anime2['mediaListEntry'] = {'status' : curr_status}

                        break

            Path = valManip.getPath() + "data.txt"

            curr = 95
            print(str(int(progress)) + "% done", end="\r")

            with open(Path, "r+") as json_file:
                json.dump(animeData, json_file, indent = 4, ensure_ascii = True)

            curr = 100
            print(str(int(progress)) + "% done", end="\r")

        elif(animeName is not None or status is not None):

            animeData = animeList.getAnimeList("FULL")
            
            for anime in animeData:

                title = anime['title']

                if(title == animeName):
                    anime['mediaListEntry'] = {'status' : status}
                    break

            Path = valManip.getPath() + "data.txt"
            with open(Path, "r+") as json_file:
                json.dump(animeData, json_file, indent = 4, ensure_ascii = True)

        

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
            
            if(len(listAll[x]) == 0): #moves to the next list if list does not exist (user has no anime in that
                                      #list)
                continue
            
            aniListLen = len(listAll[x]['entries'])
            print(aniListLen)

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
            return animeListAll
        elif(status == "FULL"):
            return AniListCalls.getAllAnime()

        return None

        pass

    def getTitleList(status):
        '''returns a list containing only the names of the anime'''
        
        #gets correct list
        animeListStat = []
        try:
            animeListStat = animeList.getAnimeList(status)['entries']
        except TypeError:
            return []

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

    




        #returns json data of anime
        animeData = (AniListAccess.getData(query, variables))['data']['Media']

        return animeData

    def getAnimeListDet(sort=None):
        global animeListDet

        if(animeListDet == [] or sort is not None):
            animeListDet = animeList.updateAnimeListDet(sort=sort)
        return animeListDet



    def getEntryId(animeName = None, anime_id = None):
        '''gets list entry ID (required to change anything related to the anime on the website)'''
        global animeListAll

        if(animeName is not None):
            aniLoc = Search.bSearchAnimeList(animeListAll, animeName=animeName)
        
        elif(anime_id is not None):
            aniLoc = Search.bSearchAnimeList(animeListAll, anime_id=anime_id)

        if(aniLoc == None): #return None if the anime is not in any of the lists
            return None
        else:	
            entryId = aniLoc['id'] #gets the entry ID of the specific anime in the list
            return entryId

    def getMediaId(animeName):

        return AniListCalls.getAnimeSearch(animeName)['id']







