import AniListAPI.animeList
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
from tqdm import tqdm, trange
import neuralNetwork.compileData


class recommendations(object):
    """description of class"""

    def findReccomended():
        '''uses neural network to recommend anime. A list of anime is returned sorted from best to worst. It is not recommended to use this due to the insane amount of inputs relative to the amount of anime a person watches'''

        animeListDet = animeList.updateAnimeListDet() #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer

        #print(animeListDet)
        
        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status
            if(animeListDet[status]['status'] == "PLANNING"):
                detListPTW = animeListDet[status]['entries']

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0

        tagListStat = {}
        tagTotal = 0

        nnRec = recNeuralNet()

        for detList in animeListDet: #iterates through each anime list type

            if(detList['status'] == "PLANNING"):
                continue

            detList = detList['entries']

            for detAnime in detList: #iterates through anime list
                
                userScore = detAnime['media']['mediaListEntry']['score']
                scoreValue = userScore - 7 #userScore is used in genre/tag value calculations. Greater than 7 is beneficial for genre/tags and less than 7 is not


                for genres in detAnime['media']['genres']: #calculate total values of the genres for the anime

                    genreValue = scoreValue

                    if genres not in genreListStat:
                        genreListStat[genres] = [genreValue]
                    else:
                        oldGenreVal = genreListStat.get(genres)
                        np.append(genreListStat[genres], genreValue)

                    genreTotal += genreValue

                for tags in detAnime['media']['tags']: #calculates total values of the tags for the anime

                    tagRank =  tags['rank']
                    tagTitle = tags['name']
                    tagValue = scoreValue * tagRank/100

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = [tagValue]
                    else:
                        np.append(tagListStat[tagTitle], tagValue)

                    tagTotal += tagValue

                animeScore = detAnime['media']['averageScore'] #score for the anime across all anilist users

                if(animeScore != None and userScore != 0):
                    nnRec.add(genreTotal, tagTotal, animeScore, userScore) #adds the genreValue, tagValue, animeScore, and userScore to the neural network data

                genreTotal = 0
                tagTotal = 0


            for genres in genreListStat: #gets the mean of the genreValues for each genre
                genreListStat[genres] = np.mean(genreListStat[genres])

            for tags in tagListStat:
                tagListStat[tags] = np.mean(tagListStat[tags])
            
            listRec = {} #animeName and their corresponding nnScore will be stored here

            max_iter = len(detListPTW) #for loading bar
            bar = tqdm(desc = "loading...", total=max_iter) #for loading bar

        nnRec.train() #trains the neural network based on the given data set

        nnRec.test()

        for anime in detListPTW:

            animeName = anime['media']['title']['userPreferred']
            animeScore = anime['media']['averageScore']
            genreValue = 0
            tagValue = 0

            if(animeScore is not None): #if the anime has released (it has been scored by other people), get score prediction

                for genres in anime['media']['genres']:

                    if genres in genreListStat:
                        genreValue += genreListStat[genres]

                for tags in anime['media']['tags']:
                    tagTitle = tags['name']
                    
                    if tagTitle in tagListStat:
                        tagValue += tagListStat[tagTitle]

                nnScore = nnRec.predict(genreValue, tagValue, animeScore)
                print(animeName + ": ")
                print("      genreValue: " + str(genreValue))
                print("        tagValue: " + str(tagValue))
                print("      animeScore: " + str(animeScore))
                print("         nnScore: " + str(nnScore))
                #print(nnScore)

                listRec[animeName] = nnScore

            #bar.update(1)
        
        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest to lowest

        print(sortedRec)

        for x in range(0,len(sortedRec)): #puts the list in a presentable format
            sortedRec[x] = sortedRec[x][0]

        return sortedRec

    def findReccomendedLegacy():
        '''Original recommendation algorithm. Hand crafted based on the score, tags, and genres of an anime based on the anime you have already watched. Returns a sorted Plan to Watch list'''

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
                        genreListStat[genres] = [genreValue]
                        genreListCount.setdefault(genres, 1)
                    else:
                        oldGenreVal = genreListStat.get(genres)
                        genreListStat[genres].append(genreValue)
                        genreListCount[genres] += 1

                    genreTotal += genreValue

                for tags in detAnime['media']['tags']:

                    tagRank =  tags['rank']
                    tagTitle = tags['name']
                    tagValue = scoreValue * tagRank/100

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = [tagValue]
                        tagListCount[tagTitle] = 1
                    else:
                        tagListStat[tagTitle].append(tagValue)
                        tagListCount[tagTitle] += 1

                    tagTotal += tagValue

            for genres in genreListStat: #applies variability equation to the genre scores

                currGenre = sorted(genreListStat[genres])

                if(len(currGenre) < 2):
                    genreListStat[genres] = 1
                    continue

                midPoint = int(len(currGenre)/2)
                median = currGenre[midPoint]
                total = np.sum(currGenre)

                if(median >= 0):
                    #genreListStat[genres] = (genreListStat[genres]/genreListCount[genres]) + 1
                    genreListStat[genres] = (median + 1) * (1 + (total/2)/genreTotal)
                else:
                    #genreListStat[genres] = 1/((abs(genreListStat[genres]/genreListCount[genres] - 1)))
                    genreListStat[genres] = 1/abs(median - 1) * ((1 + (total/2)/genreTotal))

            for tags in tagListStat:

                currTag = sorted(tagListStat[tags])
                if(len(currTag) < 2):
                    tagListStat[tags] = 0
                    continue
                midPoint = int(len(currTag)/2)
                print(tags)
                median = currTag[midPoint]
                total = np.sum(currTag)

                if(median >= 0):
                    tagListStat[tags] = math.sqrt(median) * (1 + (total/2)/tagTotal)
                else:
                    tagListStat[tags] = math.sqrt(abs(median)) * -1 * (1 + (total/2)/tagTotal)
        
            #print(genreListStat)
            #print(tagListStat)
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

                if(animeMultiplier >= 1.3 or animeMultiplier <= 1):
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

