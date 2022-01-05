from neuralNetwork.compileData import *
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

class recNeuralNet:
    """description of class"""

    data = []
    goal = []
    detListTotal = []
    newModel = False

    def __init__(self):
        global model, newModel

        try: #loads saved model. If it does not exist or is corrupted or something, then a new one is created.
            model = keras.models.load_model("nnWeights/recommendations")
            newModel = False

        except:
            #creates the neural network with the layers
            model = keras.Sequential(
                        [
                        layers.Dense(80, name="layer1", activation="relu"),
                        layers.Dense(80, name="layer1", activation= "relu"),
                        layers.Dense(160, name="layer2", activation= "relu"),
                        layers.Dense(60, name="layer3", activation= "relu"),
                        layers.Dense(40, name = "layer4", activation = "relu"),
                        layers.Dense(1, name = "layer5")
                        ]
                    )
            newModel = True
       

        #model = keras.Model(inputs = inputs, outputs = output)

    def add(self, genreValue, tagValue, recValue, animeScore , userScore):
        '''appends the genreValue, tagValue, and Scores from the anime into the data'''
        global data, goal

        self.data.append(float(genreValue))
        self.data.append(float(tagValue))
        self.data.append(float(recValue))
        self.data.append(float(animeScore))


        self.goal.append(userScore * 10)

    def addDataSet(self, user):
        global detListTotal

        animeListDet = animeList.updateAnimeListDet(user)

        for status in range(0 , len(animeListDet)): #seperates entries of lists into Completed and Planning status
            if(animeListDet[status]['status'] == "PLANNING"):
                detListPTW = animeListDet[status]['entries']

        genreTagStats = recNeuralNet.getGenreTagStats(animeListDet)

        print(genreTagStats)

        genreListStat = genreTagStats[0]
        tagListStat = genreTagStats[1]
        recListStat = genreTagStats[2]




        for detList in animeListDet:
              
            if(detList['status'] == "PLANNING"):
                  continue

            detList = detList['entries']

            for detAnime in detList: #iterates through anime list
                
                try:
                    userScore = detAnime['media']['mediaListEntry']['score']
                except TypeError:
                    continue

                animeScore = detAnime['media']['averageScore']
                genreValue = 0.0
                tagValue = 0.0

                for genres in detAnime['media']['genres']:
                    try:
                        if genres in genreListStat:
                            for genreScore in genreListStat[genres]:
                                genreValue += genreScore
                    except:
                        continue

                for tags in detAnime['media']['tags']:

                    tagTitle = tags['name']
                    
                    try:
                        if tagTitle in tagListStat:
                            for tagScore in tagListStat[tagTitle]:
                                tagValue += tagScore
                    except:
                        continue

                try:
                    if animeName in recListStat:
                        recValue = np.sum(recListStat[animeName])
                except:
                    recValue = 0
                



                    

                if(animeScore != None and userScore != 0):
                    print(valManip.sqrtKeepNeg(genreValue))
                    self.add(float(valManip.sqrtKeepNeg(genreValue)), float(valManip.sqrtKeepNeg(tagValue)), recValue, animeScore, userScore) #adds the genreValue, tagValue, animeScore, and userScore to the neural network data
                    genreValue = 0
                    tagValue = 0

    def getGenreTagStats(animeListDet):

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0
        tagListStat = {}
        tagTotal = 0
        recListStat = {}

        
        for detList in animeListDet: #iterates through each anime list type

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            detList = detList['entries']

            for detAnime in detList: #iterates through anime list
                
                try:
                    userScore = detAnime['media']['mediaListEntry']['score']
                except TypeError:
                    continue

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

                print(detAnime)

                for recommendation in detAnime['media']['recommendations']['edges']:
                    recommendation = recommendation['node']

                    try:
                        rating = recommendation['rating']
                        title = recommendation['mediaRecommendation']['title']['userPreferred']
                    except:
                        continue

                    if(rating <= 0):
                        continue
                    if(rating > 10):
                        rating = 50


                    recValue = scoreValue * (rating ** 0.25)

                    if title not in recListStat:
                        recListStat[title] = np.array(recValue)
                    else:
                        recListStat[title] = np.append(recListStat[title], recValue)

                animeScore = detAnime['media']['averageScore'] #score for the anime across all anilist users

            return [genreListStat, tagListStat, recListStat]



    def train(self):
        global model, data, goal

        self.data = np.array(self.data)
        self.data = np.reshape(self.data, (-1,4))
        self.goal = np.array(self.goal)
        self.goal = np.reshape(self.goal, (-1,1))

        print(self.data)
        print(self.goal)


        opt = tf.keras.optimizers.Adam(learning_rate=0.001)

        model.compile(loss='mse', optimizer= 'adam', metrics=["accuracy"])
        
        model.fit(self.data, self.goal,batch_size= 35, epochs = 10000)
        model.save("nnWeights/recommendations")

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

        print(animeInfo)

        animeValues = model.predict(animeInfo)

        return animeValues

    def test(self):
        print(self.data)
        prediction = model.predict(self.data)
        print(model.predict(self.data))

        diff = self.goal - prediction
        print(diff)

    def isNewModel(self): #returns in a new model was created or not when object was created
        global newModel

        return newModel
        
