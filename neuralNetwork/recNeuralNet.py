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

        #where the weights are stored
        checkpoint_path = "nnWeights/Reccomendations/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path) 

        #creates the neural network with the layers
        inputs = keras.Input(shape=(316,))
        x = layers.Dense(80, name="layer1", activation= "relu")(inputs)
        x = layers.Dense(360, name="layer2", activation= "relu")(x)
        x = layers.Dense(150, name="layer3", activation= "relu")(x)
        x = layers.Dense(50, name="layer4", activation= "relu")(x)
        output = layers.Dense(1, name="predictions", activation= "relu")(x)


        model = keras.Model(inputs = inputs, outputs = output)

        if(os.path.exists(checkpoint_dir)):
            model.load_weights(checkpoint_path)

    def add(self, genreTags, averageScore, userScore):
        '''appends the genre, tags, and score from the anime into the data'''
        global data, goal


        for genre in genreTags[0]:
            self.data.append(genre)

        for tag in genreTags[1]:
            self.data.append(tag)

        self.data.append(averageScore)
        self.goal.append(userScore)

    def train(self):
        global model, data, goal

        self.data = np.array(self.data)
        self.data = np.reshape(self.data, (-1,316))
        self.goal = np.array(self.goal)
        self.goal = np.reshape(self.goal, (-1,1))

        #where the weights are stored
        checkpoint_path = "nnWeights/Reccomendations/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)

        #data saved every 100 iterations
        cp_callback = [tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 save_freq= 100*32,
                                                 verbose=1
                                                 ),
                       tf.keras.callbacks.EarlyStopping(monitor = 'loss', min_delta = 0.001, patience = 500)]

        model.compile(loss='mse', optimizer= 'adam')
        
        model.fit(self.data, self.goal, epochs = 1000, callbacks = [cp_callback])

    def predict(self, genreTags, averageScore):
        global model

        testData = []
        
        for genre in genreTags[0]:
            testData.append(genre)

        for tag in genreTags[1]:
            testData.append(tag) 

        testData.append(averageScore)

        testData = np.array(testData)
        testData = np.reshape(testData, (-1,316))

        animeValue = model.predict(testData)

        return animeValue
        
