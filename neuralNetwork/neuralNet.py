from neuralNetwork.compileData import *
import os
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers


class neuralNet(object):
    """description of class"""
    
     

    def initialize():
        global model
        global modelNoImpact

        #where the weights are stored
        checkpoint_path = "nnWeights/Main/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path) 

        #creates the neural network with the layers
        model = keras.Sequential(
            [
            layers.Dense(40, name="layer1", activation= "relu"),
            layers.Dense(80, name="layer2", activation= "relu"),
            layers.Dense(10, name="layer3", activation= "relu"),
            layers.Dense(1, name = "layer4")
            ]
        )

        if(os.path.exists(checkpoint_dir)):
            model.load_weights(checkpoint_path)


        checkpoint_path = "nnWeights/NoImpact/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)

        modelNoImpact = keras.Sequential(
            [
            layers.Dense(40, name="layer1", activation= "relu"),
            layers.Dense(80, name="layer2", activation= "relu"),
            layers.Dense(10, name="layer3", activation= "relu"),
            layers.Dense(1, name = "layer4")
            ]
        )

        if(os.path.exists(checkpoint_dir)):
            modelNoImpact.load_weights(checkpoint_path)




    def train(iterations, cont, hasImpactRating=True):

        global model
        

        data = compileData.getSets() #gets the scores and data from all the anime

        stats = np.array(data[0]) #episode count, avg score, impact score, base speed deviation, score deviation
        realScores = np.array(data[1]) #real score 
        
       

        #where the weights are stored
        checkpoint_path = "nnWeights/Main/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path) 

        print("here")

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
        )

        #compiles model
        model.compile(loss='mse', optimizer= 'adam')

        #pretty much has neural network try to link stats with real score
        model.fit(stats, realScores, epochs = iterations, callbacks = [cp_callback])

        print(model.predict(stats))



    def trainNoImpact(iterations, cont):
        
        global modelNoImpact

        data = compileData.getSetsNoImpact() #gets the scores and data from all the anime

        stats = np.array(data[0]) #episode count, avg score, impact score, base speed deviation, score deviation
        realScores = np.array(data[1]) #real score 
        
       

        #where the weights are stored
        checkpoint_path = "nnWeights/NoImpact/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path) 

        print("here")

        batch_size = 32

        #data saved every 100 iterations
        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 save_freq= 100*batch_size,
                                                 verbose=1
                                                 )

        #if weights were saved previously, they are loaded
        if(os.path.exists(checkpoint_dir) and cont == True):
            modelNoImpact.load_weights(checkpoint_path)
        elif(cont == False):
            modelNoImpact = keras.Sequential(
            [
            layers.Dense(40, name="layer1", activation= "relu"),
            layers.Dense(80, name="layer2", activation= "relu"),
            layers.Dense(10, name="layer3", activation= "relu"),
            layers.Dense(1, name = "layer4")
            ]
        )

        #compiles model
        modelNoImpact.compile(loss='mse', optimizer= 'adam')

        #pretty much has neural network try to link stats with real score
        modelNoImpact.fit(stats, realScores, epochs = iterations, callbacks = [cp_callback])




    def predict(stats):
        '''returns neural network prediction based on the stats of an anime'''

        global model

        stats = np.array(stats)
        stats = np.reshape(stats, (-1,5))

        return model.predict(stats)

    def predictNoImpact(stats):

        global modelNoImpact

        stats = np.array(stats)
        stats = np.reshape(stats, (-1,4))

        return modelNoImpact.predict(stats)

