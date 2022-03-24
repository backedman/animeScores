from neuralNetwork.compileData import *
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import traceback

class recNeuralNet:
    """description of class"""

    data = []
    goal = []
    detListTotal = []
    new_model = False

    def __init__(self):
        global model, new_model

        checkpoint_path = "nnWeights/recommendations/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)

        model = keras.Sequential(
                        [
                        layers.Dense(80, name="layer1", activation="relu"),
                        layers.Dense(160, name="layer2", activation= "relu"),
                        layers.Dense(60, name="layer3", activation= "relu"),
                        layers.Dense(40, name = "layer4", activation = "relu"),
                        layers.Dense(1, name = "layer5")
                        ]
                    )

        if(os.path.exists(checkpoint_dir)): #loads saved weights. If it does not exist, then a new one is created.
            model.load_weights(checkpoint_path)
            new_model = False
        else:
            new_model = True

        #model = keras.Model(inputs = inputs, outputs = output)

    def add(self, genreValue, tagValue, recValue, animeScore , userScore):
        '''appends the genreValue, tagValue, and Scores from the anime into the data'''
        global data, goal

        self.data.append(float(genreValue))
        self.data.append(float(tagValue))
        self.data.append(float(recValue))
        self.data.append(float(animeScore))


        self.goal.append(userScore)

    def addDataSet(self, user):
        global detListTotal

        #get lists from given user
        userLists = AniListCalls.retAnimeListDet(user=user, sort="FINISHED_ON")

        #get genre, tag, and rec stats from the lists
        stats = recNeuralNet.getGenreTagValues(remove_outliers = True, animeListDet=userLists)
        genreListStat = stats[0]
        tagListStat = stats[1]
        tagRankStat = stats[2]
        recListStat = stats[3]



        #process the retrived values for each anime to get genre, tag, and rec values for each anime (as well as user score)
        genre_means, tag_means = recNeuralNet.calcMeans(genreListStat, tagListStat, tagRankStat)

        #print(genre_means)

        #get genre, tag, and rec values for each anime
        values = recNeuralNet.calcValues(genre_means, tag_means, recListStat, userLists)

        
        for data in values.values():

            score = data[0]
            genreVal = data[1]
            tagVal = data[2]
            recVal = data[3]
            scoreValue = data[4]
            #print(data)

            self.add(genreVal, tagVal, recVal, score, scoreValue)


                
    def calcMeans(genreListStat, tagListStat, tagRankStat):
                #get the genre_means, tag_means, and the rec_values from the user

        start = time.time()

        genre_means = {}
        tag_means = {}

        progress = 30
        #print(str(int(progress)) + "% done", end="\r")

        slices = 10/len(genreListStat)
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
               The weighting of the anime goes from 3x to the most recent anime down to 1x for the oldest
               anime in the genre. The weighting only applies to up to the most recent 30 anime completed.
               Everything older than the 30 anime will have 1x weighting.
               If there is less than 20 anime in the genre, the weighting starts from 2x.
               If there is less than 10 anime in the genre, the weighting starts from 1.5x'''
            max = 3 if size > 20 else 2 if size > 10 else 1.5
            min = 1
            size = 30 if size > 30 else size
            slice_size = (max-min)/size
            curr = max
            
            slices2 = slices/len(genre_vals)


            for score in reversed(genre_vals):
                total += valManip.powKeepNeg(score - average,2) * curr
                weighted_count += curr

                progress += slices2
                #print(str(int(progress)) + "% done", end="\r")
                
                
                if(curr > 1):
                    curr -= slice_size

            weighted_average = valManip.powKeepNeg(total/weighted_count,0.5)
            

            #scale the value so it would rarely go over 2
            if(weighted_average > 0):
                weighted_average /= 5/2
            else: #scale the value so it would rarely go under -2/3
                weighted_average /= 15/2

            genre_means[genre_title] = weighted_average

        genre_time = time.time() - start

        start = time.time()
        slices = 10/len(tagListStat)

        #get the average of each tag, with the weighting being based on the tag ranks
        for tag_title in tagListStat:

            tag_vals = tagListStat[tag_title]
            tag_ranks = tagRankStat[tag_title]

            progress += slices
            #print(str(int(progress)) + "% done", end="\r")
            

            try:
                size = len(tag_vals)
            except:
                size = 1
                tag_vals = [tagListStat[tag_title]]
                tag_ranks = [tagRankStat[tag_title]]

            tag_vals = numpy.subtract(tag_vals, average)

            weighted_average = numpy.average(tag_vals, weights=tag_ranks)

            #apply the variable log multiple to add more weight to tags that have been more prevalent
            if(size > 10):
                multi = math.log(size, 12)
            else:
                multi = (1/18) * size + (4/9)

            weighted_average *= multi

            #scale the value so it would rarely go over 1
            if(weighted_average > 0):
                weighted_average /= 5
            else: #scale the value so it would rarely go below -0.5x
                weighted_average /= 10


            tag_means[tag_title] = weighted_average

        return (genre_means, tag_means)

    def calcValues(genre_means, tag_means, recListStat, animeLists):
        
        list_rec = {}
        start = time.time()

        slices = 10/len(animeLists)

        for detList in animeLists: #iterates through each anime list

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            status = detList['status']

            detList = detList['entries']
            
            slices2 = slices/len(detList)

            for anime in detList: #iterates through each anime and finds the genreValues and tagValues

                anime = anime['media']

                try:
                    scoreValue = anime['mediaListEntry']['score']
                except:
                    continue

                title = anime['title']['userPreferred']
                score = anime['averageScore']

                if(score is None or scoreValue is 0):
                    continue

                #get genre values
                genreVal = 1

                for genre in anime['genres']:
                    try:
                        genreVal *= (1 + genre_means[genre])
                    except:
                        pass
                        #print("%s genre excluded/ignored" % genre)

                #get tag value
                tagVal = 1
                for tag in anime['tags']:
                    tag_title = tag['name']
                    tag_rank = tag['rank']
                    try:
                        tagVal *= (1 + (tag_means[tag_title] * (tag_rank/100)))
                    except:
                        pass
                        #print("%s tag exclused/ignored" % tag_title)

                #get user recommendations
                recVal = 1
                if title in recListStat:
                    for values in recListStat[title]:
                        #print(values)
                        recVal *= 1 + ((values[0] * (values[1] - average)/5))

                else:
                    pass
                    #print("%s has no user recommendations" % title)

                list_rec[title] = [score, genreVal, tagVal, recVal, scoreValue] #store all the values inside a dict

        return list_rec

    def getGenreTagValues(remove_outliers = False, animeListDet=None, progress_bar_start=0, progress_bar_end=100):
        global average

        #true_start = time.time()
        progress = progress_bar_start
        #print(str(int(progress)) + "% done", end="\r")


        start = time.time()

        if(animeListDet == None):
            animeListDet = animeList.getAnimeListDet(sort="FINISHED_ON") #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer

        progress += (progress_bar_end - progress_bar_start) * 0.05
        print(str(int(progress)) + "% done", end="\r")

        #detListPTW = AniListCalls.getAllAnime(True)
        end = time.time()

        print("execution time to get All Anime: " + str(end-start))

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}

        tagListStat = {}
        tagRankStat = {}

        recListStat = {}

        animeCount = 0
        totalScore = 0

        start = time.time()

        slices = (progress_bar_end - progress_bar_start) * 0.9/len(animeListDet)
        
        for detList in animeListDet: #iterates through each anime list

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            status = detList['status']

            detList = detList['entries']
            animeCount += len(detList)
            
            slices2 = slices/len(detList)

            for detAnime in detList: #iterates through each anime and finds the genreValues and tagValues

                try:
                    scoreValue = detAnime['media']['mediaListEntry']['score']

                except:
                    animeCount -= 1
                    continue

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

                rating_values = np.array([])
                titles = np.array([])

                for recommendation in detAnime['media']['recommendations']['edges']:
                    recommendation = recommendation['node']

                    try:
                        rating = recommendation['rating']
                        title = recommendation['mediaRecommendation']['title']['userPreferred']
                    except:
                        continue

                    if(rating <= 0):
                        continue

                    rating_values = np.append(rating_values, rating)
                    titles = np.append(titles,title)

                if(len(rating_values) == 0):
                    continue

                sum = np.sum(rating_values)
                rating_values = np.reshape(np.divide(rating_values,sum), (-1))

                for i, title in enumerate(titles):
                    if title not in recListStat:
                        recListStat[title] = np.array([[rating_values[i], scoreValue]])
                    else:
                        recListStat[title] = np.vstack((recListStat[title], [rating_values[i], scoreValue]))

                progress += slices2
                #print(str(int(progress)) + "% done", end="\r")

        average = totalScore/animeCount
        #print("animeCount " + str(animeCount))
        #print("totalScore " + str(totalScore))
        #print("average " + str(average))

        end = time.time()
        iter_time = end-start




        start = time.time()
        if(remove_outliers):
            genreListStat = recNeuralNet.removeOutliers(genreListStat)
            tagListStat,tagRankStat = recNeuralNet.removeOutliers(tagListStat, weights=tagRankStat)
        end = time.time()

        progress += (progress_bar_end - progress_bar_start) * 0.05
        #print(str(int(progress)) + "% done", end="\r")

        #true_end = time.time()

        #print("execution time to iterate through each anime in list: " + str(iter_time))
        #print("execution time to remove outliers: " + str(end-start))

        return [genreListStat, tagListStat, tagRankStat, recListStat]

    def removeOutliers(dict, weights=None, std_devs=1.96):
        '''removes the outliers in the data (ok well not exactly, but it removes the values outside of the 95% confidence interval (1.96 standard deviations) 
           to prevent rogue good or bad anime to skew the data too much'''

        total_deleted = 0
        total_sum = 0
        total_size = 0

        for val in dict:

            vals = dict[val]
            
            try:
                old_len = len(vals)
            except:
                old_len = 1
                vals = [vals]

            if(old_len < 5):
                continue


            std = np.std(vals)

            if(weights is not None):
                mean = np.average(vals, weights=weights[val])
            else:
                mean = np.mean(vals)

            if(std == 0):
                continue



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

            total_sum += np.sum(vals)
            total_size += len(vals)

            deleted = old_len - len(vals)
            total_deleted += deleted

        if(weights is not None):
            return (dict, weights)
        else:
            return (dict)

    def train(self, cont=True):
        global model, data, goal

        self.data = np.array(self.data)
        self.data = np.reshape(self.data, (-1,4))
        self.goal = np.array(self.goal)
        self.goal = np.reshape(self.goal, (-1,1))

        #print(self.data)
        #print(self.goal)

                #where the weights are stored
        checkpoint_path = "nnWeights/recommendations/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path) 

        batch_size = 32

        #data saved every 100 iterations
        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 save_freq= 100*batch_size,
                                                 verbose=1
                                                 )

        #if weights were saved previously, they are loaded
        if(os.path.exists(checkpoint_dir) and cont == True):
            model.load_weights(checkpoint_path)
        elif(cont == False):
            model = keras.Sequential(
            [
            layers.Dense(40, name="layer1", activation= "relu"),
            layers.Dense(80, name="layer2", activation= "relu"),
            layers.Dense(10, name="layer3", activation= "relu"),
            layers.Dense(1, name = "layer4")
            ]
        )#compiles model
        model.compile(loss='mse', optimizer= 'adam')



        #pretty much has neural network try to link stats with real score
        model.fit(self.data, self.goal, epochs = 20000, callbacks = [cp_callback])

    def predict(self, genreValue, tagValue, recValue, animeScore):
        global model

        testData = [genreValue, tagValue, recValue, animeScore]

        testData = np.array(testData)
        testData = np.reshape(testData, (-1,4))

        animeValue = float(model.predict(testData))
        #print(animeValue)

        return animeValue

    def predictGroup(self, animeInfo):
        global model

        animeInfo = np.reshape(animeInfo, (-1,4))

        #print(animeInfo)

        animeValues = model.predict(animeInfo)

        return animeValues

    def test(self):
        print(self.data)
        prediction = model.predict(self.data)
        print(model.predict(self.data))

        diff = self.goal - prediction
        print(diff)

    def isNewModel(self): #returns if a new model was created or not when object was created
        global new_model

        return new_model
        
