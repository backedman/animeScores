import AniListAPI.animeList
from AniListAPI.AniListAccess import *
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
from tqdm import tqdm, trange
import neuralNetwork.compileData

nnRec = recNeuralNet()

class recommendations():
    """description of class"""



    def findReccomended():
        '''uses neural network to recommend anime. A list of anime is returned sorted from best to worst. It is not recommended to use this due to the insane amount of inputs relative to the amount of anime a person watches'''
        global nnRec

        userDataSets = [AniListAccess.getUserName(), "MicchiMi", "snowwww", "Leonny", "shayoomshi", "g1appiah", "yuzurha"]

        if(nnRec.isNewModel()): #if a new model was created, train the neural net. If a new model was not created, use the previously trained network.
            for user in userDataSets:
                nnRec.addDataSet(user)

            nnRec.train()
            nnRec.test()

        stats = recommendations.getGenreTagValues()
        genreListStat = stats[0]
        tagListStat = stats[1]
        detListPTW = stats[3]

        listRec = {}
        animeInfo = np.array([])
        animeNames = np.array([])

        for anime in detListPTW:

            animeName = anime['media']['title']['userPreferred']
            animeScore = anime['media']['averageScore']
            genreValue = 0
            tagValue = 0

            if(animeScore is not None): #if the anime has released (it has been scored by other people), get score prediction

                for genres in anime['media']['genres']:

                    try:
                        if genres in genreListStat:
                            for genreScore in genreListStat[genres]:
                                genreValue += genreScore
                    except:
                        continue


                for tags in anime['media']['tags']:

                    tagTitle = tags['name']
                    
                    try:
                        if tagTitle in tagListStat:
                            for tagScore in tagListStat[tagTitle]:
                                tagValue += tagScore
                    except:
                        continue
                animeInfo = np.append(animeInfo, [float(valManip.sqrtKeepNeg(genreValue)), float(valManip.sqrtKeepNeg(tagValue)), animeScore])
                animeNames = np.append(animeNames, animeName)

                #nnScore = nnRec.predict(genreValue, tagValue, animeScore)
                print(animeName + ": ")

                #print("         nnScore: " + str(nnScore))
                #print(nnScore)

                #listRec[animeName] = nnScore

        animeInfo = np.reshape(animeInfo, (-1,3))
        results = nnRec.predictGroup(animeInfo)
        
        index = 0
        print(len(animeNames))
        print(len(results))
        for anime in animeNames:
            listRec[anime] = results[index]
            print(anime + ": ")
            print("      genreValue: " + str(animeInfo[index][0]))
            print("        tagValue: " + str(animeInfo[index][1]))
            print("      animeScore: " + str(animeInfo[index][2]))
            print("         nnScore: " + str(results[index]))

            index += 1


            #bar.update(1)
        
        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest to lowest

        print(sortedRec)

        for x in range(0,len(sortedRec)): #puts the list in a presentable format
            sortedRec[x] = sortedRec[x][0]

        #while True:

        #    print("TESTING")
        #    print("genreValue: ")
        #    genreVal = float(input())
        #    tagVal = float(input())
        #    score = float(input())

        #    print(nnRec.predict(genreVal, tagVal, score))

        return sortedRec

    def getGenreTagValues():

        animeListDet = animeList.getAnimeListDet() #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer
        
        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status
            if(animeListDet[status]['status'] == "PLANNING"):
                detListPTW = animeListDet[status]['entries']

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0

        tagListStat = {}
        tagTotal = 0

        animeCount = 0

        for detList in animeListDet:

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            detList = detList['entries']
            animeCount += len(detList)

            for detAnime in detList:



                scoreValue = detAnime['media']['mediaListEntry']['score'] - 7

                if((scoreValue + 7) == 0):
                    continue


                for genres in detAnime['media']['genres']:

                    genreValue = scoreValue

                    if genres not in genreListStat:
                        genreListStat[genres] = np.array(genreValue)
                    else:
                        genreListStat[genres] = np.append(genreListStat[genres], genreValue)


                for tags in detAnime['media']['tags']:

                    tagRank =  tags['rank']
                    tagTitle = tags['name']
                    tagValue = scoreValue

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = np.array(tagValue)
                    else:
                        tagListStat[tagTitle] = np.append(tagListStat[tagTitle], tagValue)

            stats = [genreListStat, tagListStat, animeCount, detListPTW]

            return stats

    def calcGenreTagValues(genreListStat, tagListStat):
        pass

    def findReccomendedLegacy():
        '''Original recommendation algorithm. Hand crafted based on the score, tags, and genres of an anime based on the anime you have already watched. Returns a sorted Plan to Watch list'''

        stats = recommendations.getGenreTagValues()
        genreListStat = stats[0]
        tagListStat = stats[1]
        animeCount = stats[2]
        detListPTW = stats[3]

        for genres in genreListStat: #applies variability equation to the genre scores

            try:
                currGenre = sorted(genreListStat[genres])
            except:
                currGenre = [genreListStat[genres]]

            #if(len(currGenre) < 2):
            #    genreListStat[genres] = 1
            #    continue

            size = len(currGenre)
            multi = (1 + ((float(size)/6)/animeCount))
            mean = np.mean(currGenre)
            print(genres + ": " + str(mean))
            mean = mean * multi / 5

            if(mean >= 0):
                #genreListStat[genres] = (genreListStat[genres]/genreListCount[genres]) + 1
                genreListStat[genres] = (mean + 1)
            else:
                #genreListStat[genres] = 1/((abs(genreListStat[genres]/genreListCount[genres] - 1)))
                genreListStat[genres] = 1/abs(mean - 1)

            
            print("      value: " + str(genreListStat[genres]))
            print("      multi: " + str(multi))
        
        #print(tagListStat)

        for tags in tagListStat:

            try:
                currTag = sorted(tagListStat[tags])
            except:
                currTag = [tagListStat[tags]]
                #print(currTag)

            #if(len(currTag) < 2):
            #    tagListStat[tags] = 0
            #    continue
            midPoint = int(len(currTag)/2)
            median = currTag[midPoint]
            size = len(currTag)
            
            multi = (1 + ((size/6)/animeCount))
            mean = np.mean(currTag) * multi / 5

            if(mean >= 0):
                tagListStat[tags] = math.sqrt(mean)
            else:
                tagListStat[tags] = math.sqrt(abs(mean)) * -1

            print(tags + ": " + str(mean))
            print("      multi: " + str(tagListStat[tags]))
        
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
                        animeMultiplierTag += tagListStat[tagTitle]/10
                
                    if animeMultiplierTag < 1:
                        animeMultiplierTag = abs(1/animeMultiplierTag)

                animeMultiplier = animeMultiplierGenre * animeMultiplierTag

                if(animeMultiplier >= 1.3 or animeMultiplier <= 1):
                    try:
                        animeMultiplier = math.pow(animeMultiplier, 1/3)
                    except:
                        print(animeMultiplier)

                print("      name: " + str(anime['media']['title']['userPreferred']))
                print("genres" + str(anime['media']['genres']))
                print("animeScore: " + str(animeScore))
                print("animeMultiplier: " + str(animeMultiplier))
                animeValue = animeMultiplier * anime['media']['averageScore']
            
                listRec[anime['media']['title']['userPreferred']] = animeValue

        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True)

        for x in range(0,len(sortedRec)):
            print(sortedRec[x][0] + ": " + str(sortedRec[x][1]))
            sortedRec[x] = sortedRec[x][0]

        return sortedRec

