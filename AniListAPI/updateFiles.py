from AniListAPI.animeList import *
from anime.animeFile import *

class updateFiles():
    '''the class serves the purpose of manipulating and moving files'''

    def massUpdateNNScore():
        '''updates the Neural Network scores in each file based on current weights'''

        #gets the individaul stats used for neural network score predictions (episode count, average score, speed, etc.)
        animeStats = compileData.getSetsAll(skipNoScores = False)
        data = animeList.getAnimeList("ALL")['entries']
        stats = animeStats[0]

        #uses the stats to create predictions
        predictions = neuralNet.predict(stats)

        y = 0 #amount of files that are valid for score/NN prediction (all anime with an Impact Rating). This value is incremented each time a valid anime file is accessed

        for x in range(0, len(data)):

            #gets the name and status of the anime
            animeName = data[x]['media']['title']['userPreferred']
            status = data[x]['media']['mediaListEntry']['status']

            #uses the name and status to find the file and checks if it exists
            Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
            exists = os.path.exists(Path)

            #if the file exists, then its contents are pulled and its current NN score is compared with the NN score of the new prediction
            if(exists):
                with open(Path, "r") as json_file: #opens each files and reads them
                    contents = json.load(json_file)
                    impactRating = contents['Info']['Impact Rating']

                    #anime without an impact rating aren't updated/scored, and are skipped
                    if(impactRating == -1):
                        continue

                    #update the NN score in the file based on the predicted value
                    else:
                        contents['Info']['Score']['NN Score'] = valManip.round(predictions[y][0], 2)
                        print(animeName + " " + str(stats[y]))
            
                with open(Path, "w+") as json_file:

                    json.dump(contents, json_file, indent = 4, ensure_ascii = True)

                #y is iterated each time an anime is not skipped
                y += 1

    def moveAllFiles(updateInfo=False):
        '''Moves files to the correct folder. If updateInfo is true, then the file is opened and all the information within it that is retrieved from the API originally is updated'''

        statusTypes = os.listdir(valManip.getPath())
        animeListAll = animeList.getAnimeList(status="ALL")
        
        if(updateInfo == True):
            animeListDet = animeList.updateAnimeListDet("", sort = "MEDIA_ID")

        for status in statusTypes: #iterates through different statuses

            Path = valManip.getPath(status)
            files = os.listdir(Path)
            #listAll[iterator]


            for aniFileName in files: #gets name of each file

                aniFileDir = Path + aniFileName

                with open(aniFileDir, "r+") as json_file: #opens each files and reads them

                    aniFile = json.load(json_file)

                    animeName = aniFile['Info']['Anime Name']

                    aniLoc = Search.bSearchAnimeList(animeListAll, animeName, title=True) #gets the index of the anime in the animeList

                    if(aniLoc == None):
                        animeId = aniFile['Info']['Anime Name']
                        aniLoc = Search.linearSearch(animeListAll, animeId, title=False)

                    try:
                        aniListStatus = animeListAll['entries'][aniLoc]['media']['mediaListEntry']['status']
                        print(animeListAll['entries'][aniLoc])

                    except TypeError: #if the anime from file cannot be found in the data brought in from the api, it throws an error message to check for later
                        print("ERROR COULD NOT FIND " + animeName)
                        continue

                if(status != aniListStatus):

                    aniFile['Info']['Status'] = aniListStatus #changes status listed in file

                    fileName = valManip.makeSafe(animeName)

                    oPath = aniFileDir
                    nPath = valManip.getPath(aniListStatus) + fileName + ".txt"

                    os.rename(oPath, nPath) #moves file to correct directory

                    with open(nPath, "w+") as json_file:
                        json.dump(aniFile, json_file, indent = 4, ensure_ascii = True)
                
                if(updateInfo == True):
                    
                    animeFile(animeName, status, prompt=False)