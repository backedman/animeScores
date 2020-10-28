import numpy

class getData(object):
    """description of class"""

    def readFile(Path):
        with open(Path, "r") as aniFile:
            animeData = aniFile.readlines()
            
            animeInfo = []
            epData = []
            print(animeData)
            
            indCent = animeData.index("-------------------------\n")
            for x in range(0, len(animeData)):
                animeData[x] = animeData[x].replace("\n", "")
                if(x < indCent):
                    animeInfo.append(animeData[x])
                elif(x > indCent):
                    epData.append(animeData[x])
            
            splitScore(epData)
        pass

    def splitScore(epData):
        epScore = []
        epSpeed = []
        epInfo = []

        for x in range(0, epData):
            epInfo = epData[x].split("                   ")
            epScore.append(epInfo[0])
            epSpeed.append(epInfo[0]

