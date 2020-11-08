import numpy

class getData(object):
    """description of class"""

    def readFile(Path):
        with open(Path, "r") as aniFile:
            animeData = aniFile.readlines()
            
            animeInfo = []
            epData = []
            
            indCent = animeData.index("-------------------------\n")
            for x in range(0, len(animeData)):
                animeData[x] = animeData[x].replace("\n", "")
                if(x < indCent):
                    animeInfo.append(animeData[x])
                elif(x > indCent and animeData[x] != ""):
                    epData.append(animeData[x])
            Data = [animeInfo, epData]
            return Data
            
        pass

    def splitScore(epData):
        epScore = []
        epSpeed = []


        for x in range(0, len(epData)):
            print(x)
            epInfo = epData[x].split("                   ")
            epInfo[0] = epInfo[0].replace("Episode " + str(x + 1) + ": ", "")
            epScore.append(epInfo[0])
            epInfo[1] = epInfo[1].replace("Speed: ", "")
            epSpeed.append(epInfo[1])

        epData = [epScore, epSpeed]
        
        return epData

