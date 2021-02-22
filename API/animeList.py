import pathlib
import requests
import json
import webbrowser
import time
import operator
#from main import addSpacing
from API.AniListAccess import *
from runnables.config import *
from Algorithms.Sort import *
from Algorithms.Search import *
from Algorithms.valManip import *
#from neuralNetwork.compileData import *
#from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *

animeListPTW = []
animeListCompleted = []
animeListDropped = []
animeListPaused = []
animeListRepeating = []
animeListCurrent = []
animeListAll = []
listAll = []
statusTypes = []
genreTags = []

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

    def updateAnimeListDet():
        '''gets animeList from API and updates the anime list'''
        
        global animeListPTW, animeListCompleted, animeListDropped, animeListPaused, animeListRepeating, animeListCurrent, animeListAll, statusTypes
        UserID = AniListAccess.getUserID()

        #sets query to send to server. This one asks for total number of pages, total anime, name of the anime in a page, and what list the anime is in
        query = '''
        query ($userID: Int)  {
                MediaListCollection(userId : $userID,  type: ANIME) {
                    
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
            'userID' : UserID,
        }


        #requests data from API into a list 
        animeListData = AniListAccess.getData(query, variables)['data']['MediaListCollection']['lists']

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




    def changeStatus(animeName, status):
        '''changes status of anime on website'''
        

        query = '''
            mutation ($id: Int, $status: MediaListStatus) {
                SaveMediaListEntry (id: $id, status: $status) {
                    id
                    status
                }
            }
        '''

        variables = {
            'id' : animeList.getEntryId(animeName),
            'status' : status
        }

        data = (AniListAccess.getData(query, variables))
        status = data['data']['SaveMediaListEntry']['status']

        print("Status of " + animeName + " changed to " + (str)(status))

        pass

    def changeProgress(animeName, epNumber):
        query = '''
            mutation ($id: Int, $progress: Int) {
                SaveMediaListEntry (id: $id, progress: $progress) {
                    id
                    progress
                }
            }
        '''
        variables = {
            'id' : animeList.getEntryId(animeName),
            'progress' : epNumber
        }
        
        
        data = AniListAccess.getData(query, variables)

        epNum = data['data']['SaveMediaListEntry']['progress']

        print("aniList.co updated " + animeName + " progress to episode " + (str) (epNum)) #verifies to user that the anime was updated on the website
        

        pass

    def changeScore(animeName, score):

        score = (float) (valManip.round(score, 1)) #rounds score

        query = '''
            mutation ($id: Int, $score: Float) {
                SaveMediaListEntry (id: $id, score: $score) {
                    id
                    score
                }
            }
        '''

        variables = {
            'id' : animeList.getEntryId(animeName),
            'score': score
            }

        data = AniListAccess.getData(query, variables)
        score = data['data']['SaveMediaListEntry']['score']

        print("aniList.co updated " + animeName + " score to " + (str) (score))        
        

        pass

    
    def massUpdateScore():

      data = animeListAll['entries'] #accesses the necessary sub sets in list to be called throughout the rest of the method
      prefScr = config.getPrefScr()
      
      for x in range(0, len(data)):
          #gets animeName, status, and score for comparison and updates
          animeName = data[x]['media']['title']['userPreferred']
          status = data[x]['media']['mediaListEntry']['status']
          score = data[x]['media']['mediaListEntry']['score']

          Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
          exists = os.path.exists(Path)

          if(exists):
            with open(Path, "r") as json_file:
                contents = json.load(json_file)
                fileScore = contents['Info']['Score'][prefScr]

                if(fileScore != score and fileScore != 0): #if the score stored locally and the score from the account is not the same (and if there is a score available locally), the local score overrides account score
                    animeList.changeScore(animeName, fileScore)

    def massUpdateNNScore():

        data = compileData.getSets()
        stats = data[0]
        realScores = data[1]

        predictions = neuralNet.predict(stats)


        Path = valManip.getPath("COMPLETED")
        files = os.listdir(Path)

        x = 0

        for aniFileName in files:

            aniFileDir = Path + aniFileName

            with open(aniFileDir, "r+") as json_file: #opens each files and reads them

                contents = json.load(json_file)
                realScore = contents['Info']['Score']['Real Score']

                if(realScore == 0):
                    continue;
                else:
                    contents['Info']['Score']['NN Score'] = valManip.round(predictions[x][0], 2)
            
            with open(aniFileDir, "w+") as json_file:

                json.dump(contents, json_file, indent = 4, ensure_ascii = True)

            x += 1

        

    def updateAll(animeName, status, epNumber, score):
        score = (float) (valManip.round(score, 2)) #converts score into something out of 100 instead of 10 (that is how it is used in anilist)

        query = '''
            mutation ($id: Int, $status: MediaListStatus $score: Float, $progress: Int) {
                SaveMediaListEntry (id: $id, status: $status, score: $score, progress: $progress) {
                    id
                    status
                    score
                    progress
                }
            }
        '''

        variables = {
            'id' : animeList.getEntryId(animeName),
            'status' : status,
            'score': score,
            'progress' : epNumber,
            }

        data = AniListAccess.getData(query, variables)
        status = data['data']['SaveMediaListEntry']['status']
        epNum = data['data']['SaveMediaListEntry']['progress']
        score = data['data']['SaveMediaListEntry']['score']

            #verifies to user that the anime was updated on the website
        print("Status of " + animeName + " changed to " + (str)(status))
        print("aniList.co updated " + animeName + " progress to episode " + (str) (epNum))
        print("aniList.co updated " + animeName + " score to " + (str) (score))        

        pass


    def findReccomended():
        animeListDet = animeList.updateAnimeListDet() #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer

        detListComp = {} 
        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status                
            if(animeListDet[status]['status'] == "PLANNING"):
                detListPTW = animeListDet[status]['entries']
            else:
                detListComp.update(animeListDet[status]['entries'])

        nnRec = recNeuralNet()
        
        #iterates through each anime in the Completed List
        x = 0
        for detList in animeListDet:

            if(detList['status'] == "PLANNING"):
                continue

            detList = detList['entries']

            for detAnime in detList:

                #stores the genres and tags in a list
                genres = detAnime['media']['genres']
                tags = detAnime['media']['tags']
                tagRank = [0] * len(tags)
            

                #converts the tag's list of set of names to just a list of the names to make it identical in structure to the genres list
                for x in range(len(tags)):
                    tagRank[x] = tags[x]['rank']
                    tags[x] = tags[x]['name']
                

                genreTagBinary = animeList.findGenreTagBinary(genres, tags, tagRank)

                userScore = detAnime['media']['mediaListEntry']['score']
                averageScore = detAnime['media']['averageScore']

                x+=1

                print(len(genreTagBinary[0]) + 1 + len(genreTagBinary[1]))

                nnRec.add(genreTagBinary, averageScore, userScore)


            listRec = {} #animeName and their corresponding values will be stored here
            current = 0 #for the loading bar
            total = len(detListPTW) #for loading bar

        nnRec.train()

        for anime in detListPTW:

            current += 1

            #loading bar
            percentage = valManip.round(float(current)/total * 100, 1)

            for __ in range(40):
                print("")

            print("[" + "x" * int(percentage / 5) + "-" * int(20 - percentage/5) + "]")
            print(str(percentage) + "%")


            #initializes genre and tag variables of the anime
            genres = anime['media']['genres']
            tags = anime['media']['tags']
            tagRank = [0] * len(tags)

            for x in range(len(tags)):
                tagRank[x] = tags[x]['rank']
                tags[x] = tags[x]['name']
                

            genreTagBinary = animeList.findGenreTagBinary(genres, tags, tagRank) #gets binary representation of genres and tags
            averageScore = detAnime['media']['averageScore']

            animeValue = nnRec.predict(genreTagBinary, averageScore) #gets the score assigned to anime from the neural network (higher = better)
            
            listRec[anime['media']['title']['userPreferred']] = animeValue 


        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest to lowest

        print(sortedRec)

        for x in range(0,len(sortedRec)): #puts the list in a presentable format
            sortedRec[x] = sortedRec[x][0]

        return sortedRec

    def findGenreTagBinary(genreList, tagList, tagRank):
        global genreTags

        #if the getAllGenreTags method hasn't been called yet, it is called and the genreTags information is stored in memory

        if(genreTags == []):
            genreTags = animeList.getAllGenreTags()
        
        #creates a list for all genres, all tags, genre binary, and tag binary
        allGenres = genreTags[0]
        allTags = genreTags[1]
        genreBinary = [0] * len(allGenres)
        tagBinary = [0] * len(allTags) 


        #assigns 1 for each existing coressponding genre index
        for genre in genreList:
            index = allGenres.index(genre)

            if(index > -1):
                genreBinary[index] = 1
        
        #assigns tagRank/100 for each coressponding tag index
        for tag in range(len(tagList)):
            index = allTags.index(tagList[tag])


            if(index > -1):
                tagBinary[index] = (tagRank[tag]/100)

        genreTagBinary = [genreBinary, tagBinary]

        return genreTagBinary

    def findReccomendedLegacy():
        animeListDet = animeList.updateAnimeListDet() #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer

        #print(animeListDet)
        
        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status
            if(animeListDet[status]['status'] == "PLANNING"):
              detListPTW = animeListDet[status]['entries']

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreListCount = {}
        genreTotal = 0

        tagListStat = {}
        tagListCount = {}
        tagTotal = 0


        for detList in animeListDet:

            if(detList['status'] == "PLANNING"):
                continue

            detList = detList['entries']

            for detAnime in detList:

                scoreValue = detAnime['media']['mediaListEntry']['score'] - 7


                for genres in detAnime['media']['genres']:

                    genreValue = scoreValue

                    if genres not in genreListStat:
                        genreListStat.setdefault(genres, genreValue)
                        genreListCount.setdefault(genres, 1)
                    else:
                        oldGenreVal = genreListStat.get(genres)
                        genreListStat[genres] = oldGenreVal + genreValue
                        genreListCount[genres] += 1

                    genreTotal += genreValue

                for tags in detAnime['media']['tags']:

                    tagRank =  tags['rank']
                    tagTitle = tags['name']
                    tagValue = scoreValue * tagRank/100

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = tagValue
                        tagListCount[tagTitle] = 1
                    else:
                        tagListStat[tagTitle] += tagValue
                        tagListCount[tagTitle] += 1

                    tagTotal += tagValue

            for genres in genreListStat: #applies variability equation to the genre scores
                if(genreListStat[genres] >= 0):
                    #genreListStat[genres] = (genreListStat[genres]/genreListCount[genres]) + 1
                    genreListStat[genres] = (genreListStat[genres]/genreListCount[genres] + 1) 
                else:
                    #genreListStat[genres] = 1/((abs(genreListStat[genres]/genreListCount[genres] - 1)))
                    genreListStat[genres] = 1/abs(genreListStat[genres]/genreListCount[genres] - 1)

            for tags in tagListStat:
                if(tagListStat[tags] >= 0):
                    tagListStat[tags] = math.sqrt(tagListStat[tags]/tagTotal)
                else:
                    print(tags)
                    tagListStat[tags] = math.sqrt(abs(tagListStat[tags]/tagTotal)) * -1
        
            print(genreListStat)
            print(tagListStat)
            #looks through the Planning list and uses the genres as multipliers to find the closest anime
            listRec = {}
            for anime in detListPTW:
                #print(anime)
                animeMultiplierGenre = 1
                animeMultiplierTag = 1
                animeScore = anime['media']['averageScore']

                if(animeScore is not None): #if the anime has released (it has been scored by the user), add the anime's value (average score * (value of genres added together))

                    for genres in anime['media']['genres']:

                        if genres in genreListStat:
                            animeMultiplierGenre *= genreListStat[genres]

                    for tags in anime['media']['tags']:
                        tagTitle = tags['name']
                    
                        if tagTitle in tagListStat:
                            if(tagListStat[tagTitle] >= 1):
                                animeMultiplierTag += tagListStat[tagTitle]/20
                
                    animeMultiplier = animeMultiplierGenre * animeMultiplierTag

                    if(animeMultiplier >= 1.3):
                        animeMultiplier = math.pow(animeMultiplier, 1/3)

                


                    print("      name: " + str(anime['media']['title']['userPreferred']))
                    print("genres" + str(anime['media']['genres']))
                    #print("tags" + str(anime['media']['tags']))
                    print("animeScore: " + str(animeScore))
                    #print(genreListStat)
                    print("animeMultiplier: " + str(animeMultiplier))
                    animeValue = animeMultiplier * anime['media']['averageScore']
            
                    listRec[anime['media']['title']['userPreferred']] = animeValue

            sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True)

            for x in range(0,len(sortedRec)):
                print(sortedRec[x][0] + ": " + str(sortedRec[x][1]))
                sortedRec[x] = sortedRec[x][0]

            return sortedRec

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




