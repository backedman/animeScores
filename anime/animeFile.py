import pathlib
import json
import os
import math
from runnables.main import *
from runnables.config import *
from API.animeList import *
from Algorithms.numManip import *

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
    



    """makes anime file and data that will go in there"""
    def __init__(self, animeName, status):
        Path = getPath(status) + animeName + ".txt"
        
        #gets detailed information about anime from api
        aniData = animeList.getAnimeDetailed(animeName)
            #fixes errors from specific case
        if aniData['episodes'] == None:
           aniData['episodes'] = 0
        
        #creates list to store user anime data
        Data = {'Info' : {}, 'Episodes' : {}}

        #make list with base data if file does not exist
        exists = os.path.exists(Path)
        
        if not exists:
            Data['Info'] = {'Anime Name' : animeName,
                        'Status' : status,
                        'Episode Count' : {
                                'Current' : 1,
                                'Total' : aniData["episodes"]
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
        self.epTotal = Data['Info']['Episode Count']['Total']
        self.baseSpeed = Data['Info']['Base Speed']
        self.avgScore = Data['Info']['Score']['Average Score']
        self.scaledScore = Data['Info']['Score']['Scaled Score']
        self.nnScore = Data['Info']['Score']['NN Score']
        self.realScore = Data['Info']['Score']['Real Score']
        self.impactScore = Data['Info']['Impact Rating']
        self.speedChangeable = config.getSpeedChangeable()

        #Shows prompt for user
        self.userPrompt()

        #writes to file
        self.writeToFile()
        

    def userPrompt(self):
        '''prompts user with options on what to do with anime'''
        
        #initializes variables to use in method
        animeName = self.animeName
        print("here9")
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

            #updates episode count
            epCurrent += 1
            if(epTotal < epCurrent):
                epTotal = epCurrent

            #updates data list in instance
            self.Data = Data
        
            #updates values in instance
            self.epCurrent = epCurrent
            self.epTotal = epTotal

            self.writeToFile()


        pass

    def printStats(self):
        print("Average Score: " + str(self.calcAvgScore()))
        print("Scaled Score: " + str(self.calcScaledScore()))
        pass

    def calcScaledScore(self):
        '''calculates the scaled score'''

        #initializes variables
        total = 0
        Data = self.Data
        epCurrent = self.epCurrent
        impactScore = self.impactScore

        #iterates through each episode
        for x in range (1, epCurrent):

            #get episode rating and speed
            epRating = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Score'])
            speed = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Speed'])
            difference = speed - baseSpeed

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
                total += epRating + (math.log(math.abs(difference), 4) + 2)

        score = total/epCurrent

        #shifts score based on impact rating
        if(impactScore != -1):
            score += (impactScore - 5)/5 * 12/epCurrent

        #rounds score
        score = numManip.round(score, 2)
        
        #saves score
        self.scaledScore = score

        return score
                
    def calcAvgScore(self):

        #initializes variables
        epCurrent = self.epCurrent
        Data = self.Data
        total = 0

        #iterates through episodes
        
        for x in range(1, epCurrent):
            epRating = float(Data['Episodes'][x-1]['Episode ' + str(x)]['Score'])
            total += epRating

        #averages score
        score = total/epCurrent
            
        #saves score
        self.avgScore = score

        return score


    def writeToFile(self):
        '''writes data to file'''

        #updates Data values
        Path = self.Path
        Data = self.Data
        Data['Info']['Episode Count']['Current'] = self.epCurrent
        Data['Info']['Episode Count']['Total'] = self.epTotal
        Data['Info']['Base Speed'] = self.baseSpeed
        Data['Info']['Score']['Average Score'] = self.avgScore
        Data['Info']['Score']['Scaled Score'] = self.scaledScore
        Data['Info']['Score']['NN Score'] = self.nnScore
        Data['Info']['Score']['Real Score'] = self.realScore

        #writes to file
        with open(Path, "w+") as json_file:
            json.dump(Data, json_file, indent = 4, ensure_ascii = True)
        pass

pass
    

