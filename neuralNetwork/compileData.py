import json
import numpy
from AniListAPI.animeList import *
from Algorithms.valManip import *

class compileData(object):
    '''gets the training sets for the neural network using the data from the saved files'''

    def getSetsCompleted():

        #open all json files in the completed folder
        Path = valManip.getPath("COMPLETED")
        files = os.listdir(Path)


        stats = []
        realScores = []

        for fileName in files:

            fileDir = Path + fileName

            with open(fileDir, "r+") as json_file: #opens each files and reads them

                aniFile = json.load(json_file)

                realScore = compileData.getRealScore(aniFile)

                if realScore == 0:
                    continue
                else:
                    stats.append(compileData.getEpisodeCount(aniFile))
                    stats.append(compileData.getAvgScr(aniFile))
                    stats.append(compileData.getImpactScr(aniFile))
                    stats.append(compileData.getBaseSpeedDev(aniFile))
                    stats.append(compileData.getAvgEpDev(aniFile))
                    realScores.append(realScore)

        stats = numpy.array(stats)

        print(stats)

        stats = numpy.reshape(stats, (-1,5))
        realScores = numpy.array(realScores)
        realScores = numpy.reshape(realScores, (-1,1))

        data = [stats, realScores]

        return data

    def getSetsNoImpact():

        #open all json files in the completed folder
        Path = valManip.getPath("COMPLETED")
        files = os.listdir(Path)

        stats = []
        realScores = []

        for fileName in files:

            fileDir = Path + fileName

            with open(fileDir, "r+") as json_file: #opens each files and reads them

                aniFile = json.load(json_file)

                #stats.append(fileName)
                stats.append(compileData.getEpisodeCount(aniFile))
                stats.append(compileData.getAvgScr(aniFile))
                stats.append(compileData.getBaseSpeedDev(aniFile))
                stats.append(compileData.getAvgEpDev(aniFile))
                realScores.append(compileData.getRealScore(aniFile))

        stats = numpy.array(stats)
        stats = numpy.reshape(stats, (-1,4))
        realScores = numpy.array(realScores)
        realScores = numpy.reshape(realScores, (-1,1))

        data = [stats, realScores]

        return data

    def getSetsAll(skipNoScores = True):
        '''gets the statistics and data for each file we have an anime for'''


        animeInfo = animeList.getAnimeList("ALL")['entries']

        stats = []
        realScores = []

        for x in range(len(animeInfo)):

          animeName = animeInfo[x]['media']['title']['userPreferred']
          status = animeInfo[x]['media']['mediaListEntry']['status']
            
          Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
          exists = os.path.exists(Path)

          if(exists):
            with open(Path, "r+") as json_file: #opens each files and reads them

                aniFile = json.load(json_file)

                realScore = compileData.getRealScore(aniFile)
                impactRating = compileData.getImpactScr(aniFile)

                if (realScore == 0 and skipNoScores == True) or impactRating == -1:
                    continue;
                else:
                    stats.append(compileData.getEpisodeCount(aniFile))
                    stats.append(compileData.getAvgScr(aniFile))
                    stats.append(impactRating)
                    stats.append(compileData.getBaseSpeedDev(aniFile))
                    stats.append(compileData.getAvgEpDev(aniFile))
                    realScores.append(realScore)

           


        stats = numpy.array(stats)
        stats = numpy.reshape(stats, (-1,5))
        realScores = numpy.array(realScores)
        realScores = numpy.reshape(realScores, (-1,1))

        data = [stats, realScores]

        return data

    def getRealScore(aniFile):

        return valManip.round(aniFile['Info']['Score']['Real Score'] , 2)

    def getEpisodeCount(aniFile):
        '''returns the amount of episodes watched by user in the anime'''

        return aniFile['Info']['Episode Count']['Current']

    def getAvgScr(aniFile):
        '''returns the average score of the anime'''

        return valManip.round(aniFile['Info']['Score']['Average Score'] , 2)

    def getImpactScr(aniFile):
        '''returns the impact score of the anime'''

        return aniFile['Info']['Impact Rating']

    def getBaseSpeedDev(aniFile):
        '''returns the average amount the user deviated from the Base Speed'''
        
        totalDev = 0

        baseSpeed = aniFile['Info']['Base Speed']

        for x in range(0, len(aniFile['Episodes'])):

            speed = aniFile['Episodes'][x]['Episode ' + (str)(x + 1)]['Speed']
            totalDev += baseSpeed - float(speed)

        try:
            avgDev = totalDev/len(aniFile['Episodes'])

            avgDev = valManip.round(avgDev, 4)

            return avgDev

        except ZeroDivisionError:
            return 0

    def getAvgEpDev(aniFile):
        '''returns the average amount the user deviated from the Episode Average'''

        totalDev = 0

        epAvg = compileData.getAvgScr(aniFile)

        for x in range(0, len(aniFile['Episodes'])):

            score = aniFile['Episodes'][x]['Episode ' + (str)(x + 1)]['Score']
            totalDev += (epAvg - float(score)) ** 2

        try:
            avgDev = totalDev/(len(aniFile['Episodes']) - 1)
            avgDev = valManip.round(avgDev, 4)

            return avgDev

        except ZeroDivisionError:
            return 0