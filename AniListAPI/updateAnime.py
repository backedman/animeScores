from neuralNetwork.compileData import *
from neuralNetwork.neuralNet import *
from AniListAPI.animeList import *


class updateAnime(object):
    """description of class"""

    def massUpdateNNScore():
        '''updates the Neural Network scores in each file based on current weights'''

        animeStats = compileData.getSetsAll()
        data = animeList.getAnimeList("ALL")['entries']
        stats = animeStats[0]
        realScores = animeStats[1]

        predictions = neuralNet.predict(stats)

        y = 0

        for x in range(0, len(data)):

            animeName = data[x]['media']['title']['userPreferred']
            status = data[x]['media']['mediaListEntry']['status']

            Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
            exists = os.path.exists(Path)

            if(exists):
                with open(Path, "r") as json_file: #opens each files and reads them
                    contents = json.load(json_file)
                    realScore = contents['Info']['Score']['Real Score']
                    impactRating = contents['Info']['Impact Rating']

                    if(realScore == 0 or impactRating == -1):
                        continue
                    else:
                        contents['Info']['Score']['NN Score'] = valManip.round(predictions[y][0], 2)
                        print(animeName + " " + str(stats[y]))
            
                with open(Path, "w+") as json_file:

                    json.dump(contents, json_file, indent = 4, ensure_ascii = True)

                y += 1

    def massUpdateScore():
      '''updates all scores on anilist to match the ones on file'''

      data = animeList.getAnimeList("ALL")['entries'] #accesses the necessary sub sets in list to be called throughout the rest of the method
      prefScr = config.getPrefScr()
      
      for x in range(0, len(data)):
            #gets animeName, status, and score for comparison and updates

        animeName = data[x]['media']['title']['userPreferred']
        status = data[x]['media']['mediaListEntry']['status']
        score = valManip.round(data[x]['media']['mediaListEntry']['score'], 1)

        Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
        exists = os.path.exists(Path)

        if(exists):
            with open(Path, "r") as json_file:

                contents = json.load(json_file)
                
                if(status == "DROPPED" or status == "PAUSED" or status == "REPEATING" or status == "CURRENT"): #gets the relavent score stored on file
                    fileScore = valManip.round(contents['Info']['Score']['Scaled Score'], 1)
                else:
                    fileScore = valManip.round(contents['Info']['Score'][prefScr], 1)

                if(fileScore != score and fileScore != 0):
                    print("old: " + str(score) + "      " + "new: " + str(fileScore))
                    updateAnime.changeScore(animeName, fileScore)

    def updateAll(animeName, status, epNumber, score):
        '''updates the status, score, and episode number of an anime'''

        score = (float)(valManip.round(score, 2)) #converts score into something out of 100 instead of 10 (that is how it is
                                                  #used in anilist)

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
        print("aniList.co updated " + animeName + " progress to episode " + (str)(epNum))
        print("aniList.co updated " + animeName + " score to " + (str)(score))        

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

        print("aniList.co updated " + animeName + " progress to episode " + (str)(epNum)) #verifies to user that the anime was updated on the website
        

        pass

    def changeScore(animeName, score):

        score = (float)(valManip.round(score, 1)) #rounds score

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

        print("aniList.co updated " + animeName + " score to " + (str)(score))        
        

        pass      