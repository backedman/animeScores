import pathlib
import json
import os
import math
import numpy
from runnables.config import *
from AniListAPI.updateAnime import *
from AniListAPI.updateAnime import *
from Algorithms.valManip import *
from neuralNetwork.neuralNet import *

class animeFile:

    Data = []
    aniData = []
    status = ""
    animeName = ""
    Path = ""
    epCurrent = 0
    epTotal = 0
    baseSpeed = 1.0
    avgScore = 0
    scaledScore = 0
    nnScore = 0
    realScore = 0
    impactScore = -1
    speedChangeable = False
    duration = 22



    """makes anime file and data that will go in there"""
    def __init__(self, animeName, status, prompt=True):
        Path = valManip.getPath(status) + valManip.makeSafe(animeName) + ".txt"
        
        #gets detailed information about anime from api
        aniData = animeList.getAnimeDetailed(animeName)

        #fixes errors from specific case
        if aniData['episodes'] == None:
            epTotal = 0
        else:
            epTotal = aniData['episodes']
        
        #creates list to store user anime data
        Data = {'Info' : {}, 'Episodes' : {}}

        #make list with base data if file does not exist
        exists = os.path.exists(Path)
        
        if not exists:
            Data['Info'] = {'Anime Name' : animeName,
                        'Status' : status,
                        'Episode Count' : {
                                'Current' : 0,
                                'Total' : epTotal
                            },
                        'Base Speed' : config.getBaseSpeed(),
                        'Score' : {
                                'Average Score' : 0,
                                'Scaled Score' : 0,
                                'NN Score' : 0,
                                'Real Score' : 0,
                            },
                        'Impact Rating' : -1,
                        'Episode Length' : aniData['duration']
                        }
            Data['Episodes'] = list()
            with open(Path, "w+") as json_file:
                    json.dump(Data, json_file, indent = 4, ensure_ascii = True)
                    json_file.seek(0)
                    Data = json.load(json_file)

        #make list using data from file if file exists
        else:

            #opens file and stores content in json
            with open(Path, "r+") as json_file:
                Data = json.load(json_file)
        
        #gets information from json and stores it to instance
        self.Data = Data
        self.aniData = aniData
        self.status = status
        self.animeName = animeName
        self.Path = Path
        self.epCurrent = Data['Info']['Episode Count']['Current']
        self.epTotal = epTotal
        self.baseSpeed = Data['Info']['Base Speed']
        self.avgScore = Data['Info']['Score']['Average Score']
        self.scaledScore = Data['Info']['Score']['Scaled Score']
        self.nnScore = Data['Info']['Score']['NN Score']
        self.realScore = Data['Info']['Score']['Real Score']
        self.impactScore = Data['Info']['Impact Rating']
        self.duration = aniData['duration']
        self.speedChangeable = config.getSpeedChangeable()

        #Shows prompt for user
        if(prompt == True):
            self.userPrompt()

        #writes to file and updates stats 
        self.writeToFile()

        

    def userPrompt(self):
        '''prompts user with options on what to do with anime'''
        
        #initializes variables to use in method
        animeName = self.animeName
        while(True):
            #shows user options
            print("                 " + animeName)
            print("1. Record Watching Stats")
            print("2. Get Watching Stats and Ratings")
            print("3. Other Settings")
            print("x. Go back")
            
            ans = input()

            #takes user to respective methods
            if(ans == "1"):
                self.recordStats()
            
            elif(ans == "2"):
                self.printStats()

            elif(ans == "3"):
                self.Settings()

            elif(ans == "x" or ans == "X"):
                self.writeToFile()
                self.updateStats()
                break;
        pass

    def recordStats(self):
        '''gets and records per episode score and speed from user'''
        
        #initializes variables to use in method
        epCurrent = self.epCurrent
        epTotal = self.epTotal
        speedChangeable = self.speedChangeable
        baseSpeed = self.baseSpeed
        animeName = self.animeName
        Data = self.Data

        while(True):
            #asks episode score from user
            epCurrent += 1
            print("How do you rate Episode " + str(epCurrent) + " of " + str(animeName) + "?")

            epScore = input()
                #retakes and informs user if input is not valid
            while(not epScore.isdigit() and not (epScore == "x" or epScore == "X")):
                print("That is not a valid input. Please enter a number. To exit the program enter -1")
                epScore = input()

                #stops taking in episode scores if input is -1
            if(epScore == "x" or epScore == "X"):
                break

            #if config allows, ask user for speed of show
            if(speedChangeable):
               print("Speed?")

               epSpeed = input()
               #retakes and informs user if input is not valid
               while(not epScore.isdigit()):
                    print("That is not a valid input. Please enter a number.")
                    epSpeed = input()

            else:
                epSpeed = baseSpeed

            

            #adds score and speed to data
            dataToAppend = {('Episode ' + str(epCurrent)) : {'Score' : str(epScore) , 'Speed' : str(epSpeed)}}
            Data['Episodes'].append(dataToAppend)

            #updates values in instance
            self.epCurrent = epCurrent
            self.epTotal = epTotal

            #updates episode count
            updateAnime.changeProgress(animeName, epCurrent)
            self.updateScores()

            #updates data list in instance
            self.Data = Data

            self.writeToFile()


        pass

    def printStats(self):
        print("Average Score: " + str(valManip.round(self.calcAvgScore(), 2)))
        print("Scaled Score: " + str(valManip.round(self.calcScaledScore(), 2)))
        print("NN Score: " + str(valManip.round(self.calcNNScore(), 2)))
        pass

    def calcScaledScore(self):
        '''calculates the scaled score'''

        #initializes variables
        total = 0
        Data = self.Data
        epCurrent = self.epCurrent
        impactScore = self.impactScore

        #iterates through each episode
        for x in range (1, epCurrent + 1):

            #get episode rating and speed
            epRating = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Score'])
            speed = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Speed'])
            difference = speed - self.baseSpeed

            #scales the score based on speed deviation from base speed
            if(difference >= 0 and difference <= 0.25):
                total += epRating - 2 * difference

            elif (difference > 0.25 and difference <= 1):
                total += epRating - (math.log(difference, 4) + 2)

            elif(difference > 1 and difference <= 2):
                total += epRating - (difference + 1)

            elif(difference > 2):
                total += epRating - (difference/2 + 2)

            elif(difference < 0 and difference >= -0.25):
                total += (epRating - 2 * difference)

            elif(difference < -0.25 and difference >= -1):
                total += epRating + (math.log(abs(difference), 4) + 2)

        score = total/epCurrent

        #shifts score based on impact rating
        if(impactScore != -1):
            score += (impactScore - 5)/5 * 12/epCurrent
        
        #saves score
        self.scaledScore = score

        return score
                
    def calcAvgScore(self):

        #initializes variables
        epCurrent = self.epCurrent
        Data = self.Data
        total = 0

        #iterates through episodes
        for x in range(1, epCurrent + 1):
            epRating = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Score'])
            total += epRating

        #averages score
        score = total/epCurrent
            
        #saves score
        self.avgScore = score

        return score

    def getAvgEpDeviation(self):
        '''returns the average deviation of score from the average score for the anime'''

        #initializes variables
        epCurrent = self.epCurrent
        Data = self.Data
        avgScore = self.calcAvgScore()
        totalDev = 0

        for x in range(1, epCurrent + 1): #adds up the difference between the episode's score and the average score for all episodes

            epRating = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Score'])
            totalDev += (avgScore - epRating) ** 2

        try:
            avgDev = totalDev/(epCurrent - 1) #gets the average of the differences between the episode's score and average score

            avgDev = valManip.round(avgDev, 4)

            print("avg dev: " + str(avgDev))

            return avgDev
        
        except ZeroDivisionError:
            return 0;


    def getAvgSpeedDeviation(self):
        '''returns the average deviation of speed from the base speed for the anime'''

        #initialized variables
        epCurrent = self.epCurrent
        Data = self.Data
        baseSpeed = self.baseSpeed
        totalDev = 0

        for x in range(1, epCurrent + 1): #adds up the differences between the episode's speed and the base speed for all episodes

            speed = Data['Episodes'][x-1]['Episode ' + (str)(x)]['Speed']
            totalDev += float(speed) - baseSpeed

        avgDev = totalDev/epCurrent

        avgDev = valManip.round(avgDev, 4)

        print("speed dev: " + str(avgDev))

        return avgDev

    def calcNNScore(self):
        '''gets the NN score for the anime'''

        #initializes variables
        epCount = self.epCurrent
        avgScore = self.avgScore
        impactScore = self.impactScore
        baseSpeedDev = self.getAvgSpeedDeviation()
        epScoreDev = self.getAvgEpDeviation()

        print("epCount: " + str(epCount))

        #gets the nn score prediction
        if(impactScore != -1): #if show has impact rating use this version
            stats = numpy.array([epCount, avgScore, impactScore, baseSpeedDev, epScoreDev])
            stats = numpy.reshape(stats, (-1, 5))
            prediction = neuralNet.predict(stats)


        else: #if show does not have impact rating use this version
            stats = numpy.array([epCount, avgScore, baseSpeedDev, epScoreDev])
            stats = numpy.reshape(stats, (-1, 4))
            print("here")
            prediction = neuralNet.predictNoImpact(stats)

        

        self.nnScore = prediction

        return prediction
    
    def updateScores(self):

        self.avgScore = self.calcAvgScore()
        self.nnScore = self.calcNNScore()
        self.scaledScore = self.calcScaledScore()

    def Settings(self):
        '''Offers setting menu'''
        
        #initializes variables
        animeName = self.animeName

        #prompts user
        print("                 " + animeName)
        print("1. Change Status")
        print("2. Set Impact Score")
        print("3. Set Real Score")
        print("4. update Stats on website")
        print("x. Go back")

        #different actions based on user prompt
        ans = input()
            #user changes status
        if(ans == "1"):
            print("1. WATCHING")
            print("2. COMPLETED")
            print("3. PLANNING")
            print("4. DROPPED")
            print("5. PAUSED")
            ans = input()

            #status is based on user input
            if(ans == "1"):
                self.changeStatus("CURRENT")

            elif(ans == "2"):
                self.changeStatus("COMPLETED")

                print("     ")
                print("     ")
                print("     ")
                print("You Finished! You need to give it an impact score now! (type -1 if you don't want to do this)")

                self.impactScore = float(input())
                self.calcNNScore()

                self.updateStats()

            elif(ans == "3"):
                self.changeStatus("PLANNING")
            elif(ans == "4"):
                self.changeStatus("DROPPED")
            elif(ans == "5"):
                self.changeStatus("PAUSED")
        
        elif(ans == "2"):
            print("Type impact score (1-10)")
            self.impactScore = int(input())

        elif(ans == "3"):
            print("Type real score (1-10)")
            self.realScore = float(input())

        elif(ans == "4"):
            self.writeToFile()
            self.updateStats()

        pass

    def changeStatus(self, nStatus):
        
        oPath = self.Path
        nPath = valManip.getPath(nStatus) + valManip.makeSafe(self.animeName) + ".txt"

        os.rename(oPath, nPath) #moves file to correct directory

        updateAnime.changeStatus(self.animeName, nStatus) #changes anime status on user account

        #updates values
        self.status = nStatus
        self.Path = nPath

        self.writeToFile() #saves new data to file

        pass

    def writeToFile(self):
        '''writes data to file'''

        #updates Data values
        Path = self.Path
        Data = self.Data
        Data['Info']['Episode Count']['Current'] = self.epCurrent
        Data['Info']['Episode Count']['Total'] = self.epTotal
        Data['Info']['Status'] = self.status
        Data['Info']['Base Speed'] = self.baseSpeed
        Data['Info']['Score']['Average Score'] = valManip.round(self.avgScore, 2)
        Data['Info']['Score']['Scaled Score'] = valManip.round(self.scaledScore, 2)
        Data['Info']['Score']['NN Score'] = valManip.round(self.nnScore, 2)
        Data['Info']['Impact Rating'] = self.impactScore
        Data['Info']['Episode Length'] = self.duration
        Data['Info']['Score']['Real Score'] = self.realScore

        #writes to file
        with open(Path, "w+") as json_file:
            json.dump(Data, json_file, indent = 4, ensure_ascii = True)

        pass
    
    def updateStats(self):
        '''update stats of anime on website'''

        updateAnime.changeStatus(self.animeName, self.status) #updates status on website
        updateAnime.changeProgress(self.animeName, self.epCurrent) #updates episode count on website

        if(self.nnScore == 0 or self.status != "COMPLETED"): #updates score on website (scaled score is used if not completed. NN score if it is)
            updateAnime.changeScore(self.animeName, self.scaledScore)
        else:
            updateAnime.changeScore(self.animeName, self.nnScore)

        pass
    

