import AniListAPI.animeList
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
import neuralNetwork.compileData


class recommendations(object):
    """description of class"""

    def findReccomended():
        '''uses neural network to recommend anime. A list of anime is returned sorted from best to worst. It is not recommended to use this due to the insane amount of inputs relative to the amount of anime a person watches'''

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
                

                genreTagBinary = recommendations.findGenreTagBinary(genres, tags, tagRank)

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
                

            genreTagBinary = recommendations.findGenreTagBinary(genres, tags, tagRank) #gets binary representation of genres and tags
            averageScore = detAnime['media']['averageScore']

            animeValue = nnRec.predict(genreTagBinary, averageScore) #gets the score assigned to anime from the neural network (higher = better)
            
            listRec[anime['media']['title']['userPreferred']] = animeValue 


        sortedRec = sorted(listRec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest to lowest

        print(sortedRec)

        for x in range(0,len(sortedRec)): #puts the list in a presentable format
            sortedRec[x] = sortedRec[x][0]

        return sortedRec

    def findGenreTagBinary(genreList, tagList, tagRank):
        '''returns a binary representation of the genres and tags'''

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

