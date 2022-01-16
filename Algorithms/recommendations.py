import AniListAPI.animeList
import AniListAPI.AniListCalls
from AniListAPI.AniListAccess import *
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
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
        recListStat = stats[2]
        detListPTW = stats[4]

        listRec = {}
        animeInfo = np.array([])
        animeNames = np.array([])

        for anime in detListPTW:

            animeName = anime['title']['userPreferred']
            animeScore = anime['averageScore']
            genreValue = 0
            tagValue = 0
            recValue = 0

            if(animeScore is not None): #if the anime has released (it has been scored by other people), get score prediction

                for genres in anime['genres']:

                    try:
                        if genres in genreListStat:
                            genreValue = np.sum(genreListStat[genres])/math.sqrt(len(genreListStat[genres]))
                    except:
                        continue


                for tags in anime['tags']:

                    tagTitle = tags['name']
                    
                    try:
                        if tagTitle in tagListStat:
                            tagValue = np.sum(tagListStat[tagTitle])/math.sqrt(len(tagListStat[tagTitle]))
                    except:
                        continue
                
                try:
                    if animeName in recListStat:
                        recValue = np.sum(recListStat[animeName])/math.sqrt(len(recListStat[animeName]))
                except:
                    continue

                animeInfo = np.append(animeInfo, [float(valManip.sqrtKeepNeg(genreValue)), float(valManip.sqrtKeepNeg(tagValue)), recValue, animeScore])
                animeNames = np.append(animeNames, animeName)

                #nnScore = nnRec.predict(genreValue, tagValue, animeScore)
                print(animeName + ": ")

                #print("         nnScore: " + str(nnScore))
                #print(nnScore)

                #listRec[animeName] = nnScore

        animeInfo = np.reshape(animeInfo, (-1,4))
        results = nnRec.predictGroup(animeInfo)
        
        index = 0
        print(len(animeNames))
        print(len(results))
        for anime in animeNames:
            listRec[anime] = results[index]
            print(anime + ": ")
            print("      genreValue: " + str(animeInfo[index][0]))
            print("        tagValue: " + str(animeInfo[index][1]))
            print("        recValue: " + str(animeInfo[index][2]))
            print("      animeScore: " + str(animeInfo[index][3]))
            print("         nnScore: " + str(results[index]))

            index += 1


            #bar.update(1)
        
        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest to lowest

        print(sortedRec)

        for x in range(0,len(sortedRec)): #puts the list in a presentable format
            sortedRec[x] = str(sortedRec[x][0]) + "- " + str(sortedRec[x][1])

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
        detListPTW = {}

        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status
            if(animeListDet[status]['status'] == "PLANNING"):
                detListPTW = animeListDet[status]['entries']

        detListPTW = AniListCalls.getAllAnime(True)

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0

        tagListStat = {}
        tagTotal = 0

        recListStat = {}

        animeCount = 0
        totalScore = 0

        for detList in animeListDet: #iterates through each anime list

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            detList = detList['entries']
            animeCount += len(detList)


            for detAnime in detList: #iterates through each anime and finds the genreValues and tagValues

                scoreValue = detAnime['media']['mediaListEntry']['score']

                if((scoreValue) == 0):
                    continue

                totalScore += scoreValue

                for genres in detAnime['media']['genres']: #gets genreValues

                    genreValue = scoreValue

                    if genres not in genreListStat:
                        genreListStat[genres] = np.array(genreValue)
                    else:
                        genreListStat[genres] = np.append(genreListStat[genres], genreValue)


                for tags in detAnime['media']['tags']: #gets tagValues

                    tagRank =  tags['rank']
                    tagTitle = tags['name']
                    tagValue = scoreValue

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = np.array(tagValue)
                    else:
                        tagListStat[tagTitle] = np.append(tagListStat[tagTitle], tagValue)

                for recommendation in detAnime['media']['recommendations']['edges']:
                    recommendation = recommendation['node']

                    #print(recommendation)

                    try:
                        rating = recommendation['rating']
                        title = recommendation['mediaRecommendation']['title']['userPreferred']
                    except:
                        continue


                    if(rating <= 0):
                        continue
                    if(rating > 50):
                        rating = 50


                    recValue = scoreValue * (rating ** 0.25)

                    if title not in recListStat:
                        recListStat[title] = np.array(recValue)
                    else:
                        recListStat[title] = np.append(recListStat[title], recValue)

        print("average score: " + str(totalScore/animeCount))

        stats = [genreListStat, tagListStat, recListStat, animeCount, detListPTW]

        return stats

    def calcGenreTagValues(genreListStat, tagListStat):
        pass

    def findReccomendedLegacy():
        '''Original recommendation algorithm. Hand crafted based on the score, tags, and genres of an anime based on the anime you have already watched. Returns a sorted Plan to Watch list'''

        stats = recommendations.getGenreTagValues()
        genreListStat = stats[0]
        tagListStat = stats[1]
        recListStat = stats[2]
        animeCount = stats[3]
        detListPTW = stats[4]

        #weight the more newly watched animes in each genre more than the others
        genre_means = {}
        #loop through each genre
        for genre_title in genreListStat:
            
            genre_vals = genreListStat[genre_title]
            print(genre_vals)

            size = len(genre_vals)
            weighted_count = 0
            total = 0

            '''create identical slices based on the amount in the genre.
               The weighting of the anime goes from 2x to the most recent anime down to 0.5x for the oldest
               anime in the genre. If there is less than 10 anime in the genre, the weighting only goes down to 1x'''

            max = 2
            min = 1 if size <= 10 else 0.5
            slice_size = (max-min)/size
            curr = max
            
            for score in reversed(genre_vals):
                total += score * curr
                weighted_count += curr
                curr -= slice_size

            weighted_average = total/weighted_count
            genre_means[genre_title] = weighted_average

        print(genre_means)

            





        pass

