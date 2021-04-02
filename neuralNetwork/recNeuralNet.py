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

    def __init__(self):
        global model

        #creates the neural network with the layers
        inputs = keras.Input(shape=(3,))
        x = layers.Dense(40, name="layer1", activation= "relu")(inputs)
        x = layers.Dense(80, name="layer2", activation= "relu")(x)
        x = layers.Dense(10, name="layer3", activation= "relu")(x)
        output = layers.Dense(1, name="predictions", activation= "relu")(x)


        model = keras.Model(inputs = inputs, outputs = output)

    def add(self, genreValue, tagValue, animeScore, userScore):
        '''appends the genreValue, tagValue, and Scores from the anime into the data'''
        global data, goal

        self.data.append(genreValue)
        self.data.append(tagValue)
        self.data.append(animeScore)

        self.goal.append(userScore)

    def train(self):
        global model, data, goal

        self.data = np.array(self.data)
        self.data = np.reshape(self.data, (-1,3))
        self.goal = np.array(self.goal)
        self.goal = np.reshape(self.goal, (-1,1))

        print(self.data)
        print(self.goal)

        model.compile(loss='mse', optimizer= 'adam')
        
        model.fit(self.data, self.goal, epochs = 4000)

    def predict(self, genreValue, tagValue, animeScore):
        global model

        testData = [genreValue, tagValue, animeScore]

        testData = np.array(testData)
        testData = np.reshape(testData, (-1,3))

        animeValue = float(model.predict(testData))
        #print(animeValue)

        return animeValue

    def test(self):
        print(self.data)
        print(model.predict(self.data))
        
