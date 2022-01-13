from neuralNetwork.compileData import *
from neuralNetwork.neuralNet import *
from AniListAPI.animeList import *


class updateAnime():
    """description of class"""

    def massUpdateScore():
      '''updates all scores on anilist to match the ones on file'''

      data = animeList.getAnimeList("ALL")['entries'] #accesses the necessary sub sets in list to be called throughout the rest of the method
      prefScr = config.getPrefScr()
      
      for x in range(0, len(data)):
            #gets animeName, status, and score for comparison and updates

        animeName = data[x]['media']['title']['userPreferred']
        entry_id = data[x]['id']
        status = data[x]['media']['mediaListEntry']['status']
        score = valManip.round(data[x]['media']['mediaListEntry']['score'], 1)

        Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
        exists = os.path.exists(Path)

        if(exists):
            with open(Path, "r") as json_file:

                contents = json.load(json_file)
                
                if(status == "DROPPED" or status == "PAUSED" or status == "REPEATING" or status == "CURRENT" or status == "PLANNING"): #gets the relavent score stored on file
                    fileScore = valManip.round(contents['Info']['Score']['Scaled Score'], 1)
                else:
                    fileScore = valManip.round(contents['Info']['Score'][prefScr], 1)

                if(fileScore != score and fileScore != 0):
                    print("old: " + str(score) + "      " + "new: " + str(fileScore))
                    updateAnime.changeScore(score = fileScore, entry_id = entry_id)

    def updateInfo(animeName = None, animeId = None, entry_id=None, status = None, epNumber = None, score = None):
        '''updates the status, score, and episode number of an anime'''

        score = (float)(valManip.round(score, 2)) #converts score into something out of 100 instead of 10 (that is how it is
                                                  #used in anilist)



        query = '''
            mutation ($id: Int, $status: MediaListStatus, $mediaId: Int $score: Float, $progress: Int) {
                SaveMediaListEntry (id: $id, status: $status, mediaId: $mediaId, score: $score, progress: $progress) {
                    media{
                        title{
                            userPreferred
                        }
                    }
                    id
                    status
                    score
                    progress
                }
            }
        '''

        if(entry_id==None):
            if(animeName is not None):
                id = animeList.getEntryId(animeName=animeName)
            elif(animeId is not None):
                id = animeList.getEntryId(anime_id=animeId)
        else:
            id = entry_id

        #if the anime is on the list somewhere, updates the entry
        if(id != None):
            variables = {
                'id' : id,
                'progress' : epNumber,
                'score' : score,
                'status' : status
            }
        
        #if the anime is NOT on a user list, a new entry is created
        else:
            if(animeId == None):
                animeId = animeList.getMediaId(animeName)

            variables = {
                'mediaId': animeId,
                'progress' : epNumber,
                'score' : score,
                'status' : status
            }

        data = AniListAccess.getData(query, variables)
        animeName = data['data']['SaveMediaListEntry']['media']['title']['userPreferred']
        status = data['data']['SaveMediaListEntry']['status']
        epNum = data['data']['SaveMediaListEntry']['progress']
        score = data['data']['SaveMediaListEntry']['score']

            #verifies to user that the anime was updated on the website
        print("Status of " + animeName + " changed to " + (str)(status))
        print("aniList.co updated " + animeName + " progress to episode " + (str)(epNum))
        print("aniList.co updated " + animeName + " score to " + (str)(score))        

        pass

    def changeStatus(animeName = None, animeId = None, entry_id=None, status = None):
        '''changes status of anime on website'''
        

        query = '''
            mutation ($id: Int, $mediaId: Int, $status: MediaListStatus) {
                SaveMediaListEntry (id: $id, mediaId: $mediaId, status: $status) {
                    media{
                        title{
                            userPreferred
                        }
                    }
                    id
                    status
                }
            }
        '''
        
        if(entry_id==None):
            if(animeName is not None):
                id = animeList.getEntryId(animeName=animeName)
            elif(animeId is not None):
                id = animeList.getEntryId(anime_id=animeId)
        else:
            id = entry_id

        #if the anime is on the list somewhere, updates the entry
        if(id != None):
            variables = {
                'id' : id,
                'status' : status
            }
        
        #if the anime is NOT on a user list, a new entry is created
        else:
            if(animeId == None):
                animeId = animeList.getMediaId(animeName)

            variables = {
                'mediaId': animeId,
                'status' : status
            }

        data = AniListAccess.getData(query, variables)
        status = data['data']['SaveMediaListEntry']['status']

        animeName = data['data']['SaveMediaListEntry']['media']['title']['userPreferred']

        print("Status of " + animeName + " changed to " + (str)(status))

        pass

    def changeProgress(animeName = None, animeId = None, entry_id=None, epNumber = None):
        query = '''
            mutation ($id: Int, $mediaId: Int, $progress: Int) {
                SaveMediaListEntry (id: $id, mediaId: $mediaId, progress: $progress) {
                    media{
                        title{
                            userPreferred
                        }
                    }
                    id
                    progress
                }
            }
        '''
        if(entry_id==None):
            if(animeName is not None):
                id = animeList.getEntryId(animeName=animeName)
            elif(animeId is not None):
                id = animeList.getEntryId(anime_id=animeId)
        else:
            id = entry_id

        #if the anime is on the list somewhere, updates the entry
        if(id != None):
            variables = {
                'id' : id,
                'progress' : epNumber
            }
        
        #if the anime is NOT on a user list, a new entry is created
        else:
            if(animeId == None):
                animeId = animeList.getMediaId(animeName)

            variables = {
                'mediaId': animeId,
                'progress' : epNumber
            }

        data = AniListAccess.getData(query, variables)
        epNum = data['data']['SaveMediaListEntry']['progress']

        animeName = data['data']['SaveMediaListEntry']['media']['title']['userPreferred']

        print("aniList.co updated " + animeName + " progress to episode " + (str)(epNum)) #verifies to user that the anime was updated on the website
        

        pass

    def changeScore(animeName = None, animeId = None, entry_id=None, score = None):

        score = (float)(valManip.round(score, 1)) #rounds score

        query = '''
            mutation ($id: Int, $mediaId: Int, $score: Float) {
                SaveMediaListEntry (id: $id, mediaId: $mediaId, score: $score) {
                    media{
                        title{
                            userPreferred
                        }
                    }
                    id
                    score
                }
            }
        '''
        
        if(entry_id==None):
            if(animeName is not None):
                id = animeList.getEntryId(animeName=animeName)
            elif(animeId is not None):
                id = animeList.getEntryId(anime_id=animeId)
        else:
            id = entry_id

        #if the anime is on the list somewhere, updates the entry
        if(id != None):
            variables = {
                'id' : id,
                'score' : score
            }
        
        #if the anime is NOT on a user list, a new entry is created
        else:
            if(animeId == None):
                animeId = animeList.getMediaId(animeName)

            variables = {
                'mediaId': animeId,
                'score' : score
            }

        data = AniListAccess.getData(query, variables)
        score = data['data']['SaveMediaListEntry']['score']

        animeName = data['data']['SaveMediaListEntry']['media']['title']['userPreferred']

        print("aniList.co updated " + animeName + " score to " + str(score))    
        

        pass






                    