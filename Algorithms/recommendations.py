import AniListAPI.animeList
import AniListAPI.AniListCalls
from AniListAPI.AniListAccess import *
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
import neuralNetwork.compileData
import traceback
import time

nnRec = recNeuralNet()

class recommendations():
    """description of class"""

    average = None

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

    def getGenreTagValues(remove_outliers = False):
        global average

        animeListDet = animeList.getAnimeListDet() #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer
        detListPTW = {}

        true_start = time.time()

        start = time.time()
        detListPTW = AniListCalls.getAllAnime(True)
        end = time.time()

        print("execution time to get All Anime: " + str(end-start))

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0

        tagListStat = {}
        tagRankStat = {}
        tagTotal = 0

        recListStat = {}

        animeCount = 0
        totalScore = 0

        start = time.time()

        for detList in animeListDet: #iterates through each anime list

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            detList = detList['entries']
            animeCount += len(detList)



            for detAnime in detList: #iterates through each anime and finds the genreValues and tagValues

                scoreValue = detAnime['media']['mediaListEntry']['score']

                if((scoreValue) == 0):
                    animeCount -= 1
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
                    if(tagRank < 10):
                        continue
                    tagTitle = tags['name']
                    tagValue = scoreValue

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = np.array(tagValue)
                        tagRankStat[tagTitle] = np.array(tagRank)
                    else:
                        tagListStat[tagTitle] = np.append(tagListStat[tagTitle], tagValue)
                        tagRankStat[tagTitle] = np.append(tagRankStat[tagTitle], tagRank)

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

        average = totalScore/animeCount

        end = time.time()
        iter_time = end-start


        start = time.time()
        if(remove_outliers):
            genreListStat = recommendations.removeOutliers(genreListStat)
            tagListStat,tagRankStat = recommendations.removeOutliers(tagListStat, weights=tagRankStat)
        end = time.time()
        true_end = time.time()

        print("execution time to iterate through each anime in list: " + str(iter_time))
        print("execution time to remove outliers: " + str(end-start))
        print("total execution time: " + str(true_end - true_start))

                

        #print("average score: " + str(totalScore/animeCount))

        



        stats = [genreListStat, tagListStat, tagRankStat, recListStat, animeCount, detListPTW, average]

        return stats




    def removeOutliers(dict, weights=None, std_devs=1.96):
        '''removes the outliers in the data (ok well not exactly, but it removes the values outside of the 95% confidence interval (1.96 standard deviations) 
           to prevent rogue good or bad anime to skew the data too much'''

        for val in dict:

            vals = dict[val]
            #print("-------------------%s------------------------" % val)
            std = np.std(vals)



            if(weights is not None):
                mean = np.average(vals, weights=weights[val])
            else:
                mean = np.mean(vals)

            #print("old mean: " + str(mean))
            #print("std: " + str(std))

            if(std == 0):
                continue

            try:
                old_len = len(vals)
            except:
                old_len = 1
                vals = [vals]

            arr = np.array(vals)

            if(weights is not None):
                new_arr=np.array([])
                new_weights = np.array([])
                deleted = 0

                if(std is 0.0):
                    continue

                for count, x in enumerate(arr):
                    if(x > valManip.round(mean - 1.96*std,1) and x < valManip.round(mean + 1.96*std,1)):
                        new_arr = np.append(new_arr, x)
                        try:
                            new_weights = np.append(new_weights, weights[val][count])
                        except:
                            traceback.print_exc()
                            print(count)
                    else:
                        deleted += 1

                dict[val] = new_arr
                weights[val] = new_weights


            else:
                arr = np.delete(arr, np.argwhere(arr < valManip.round(mean - 1.96*std,1)))
                arr = np.delete(arr, np.argwhere(arr > valManip.round((mean + 1.96 * std),1)))
                dict[val] = arr
                
            vals = dict[val]

            if(weights is not None):
                mean = np.average(vals, weights=weights[val])
            else:
                mean = np.mean(vals)
            deleted = old_len - len(vals)
            
            #print("new mean: " + str(mean))
            #print("deleted: " + str(deleted))

        if(weights is not None):
            return (dict, weights)
        else:
            return dict

    def calcGenreTagValues(genreListStat, tagListStat):
        pass

    def findReccomendedLegacy():
        '''Original recommendation algorithm. Hand crafted based on the score, tags, and genres of an anime based on the anime you have already watched. Returns a sorted Plan to Watch list'''

        stats = recommendations.getGenreTagValues(remove_outliers=True)
        genreListStat = stats[0]
        tagListStat = stats[1]
        tagRankStat = stats[2]
        recListStat = stats[3]
        animeCount = stats[4]
        detListPTW = stats[5]
        average = stats[6]

        print("average: " + str(average))

        #weight the more newly watched animes in each genre more than the others
        genre_means = {}
        #loop through each genre
        for genre_title in genreListStat:
            
            genre_vals = genreListStat[genre_title] 

            try:
                size = len(genre_vals)
            except:
                size = 1
                genre_vals = [genreListStat[genre_title]]
            
            weighted_count = 0
            total = 0

            '''create identical slices based on the amount in the genre.
               The weighting of the anime goes from 2x to the most recent anime down to 0.5x for the oldest
               anime in the genre. If there is less than 10 anime in the genre, the weighting only goes down to 1x.
               If there is less than 5 anime in the genre, the weighting goes up to 1.5x'''
            max = 2 if size > 5 else 1.5
            min = 1 if size <= 10 else 0.5
            slice_size = (max-min)/size
            curr = max
            


            for score in reversed(genre_vals):
                total += valManip.powKeepNeg(score - average,2) * curr
                weighted_count += curr
                curr -= slice_size

            print(total)
            print(weighted_count)
            weighted_average = valManip.powKeepNeg(total/weighted_count,0.5)
            genre_means[genre_title] = weighted_average

        print(genre_means)

            





        pass

