import pathlib
import json
import os
from runnables.main import *
from runnables.config import *
from API.animeList import *

class animeFile:

    Data = []
    aniData = []
    status = ""
    animeName = ""
    Path = ""
    episodeCurrent = 0
    episodeTotal = 0
    baseSpeed = 1.0
    avgScore = 0
    scaledScore = 0
    nnScore = 0
    realScore = 0
    speedChangeable = False
    



    """makes anime file and data that will go in there"""
    def __init__(self, animeName, status):
        Path = getPath(status) + animeName + ".txt"
        
        print("here2")
        #gets detailed information about anime from api
        aniData = animeList.getAnimeDetailed(animeName)
            #fixes errors from specific case
        if aniData['episodes'] == None:
           aniData['episodes'] = 0
        
        print("here3")
        #creates list to store user anime data
        Data = json.loads(['Info', 'Episodes'])
        
        #make list with base data if file does not exist
        exists = os.path.exists(Path)
        
        print("here4")
        if not exists:
            Data['Info'].append({'Anime Name' : animeName,
                        'Status' : status,
                        'Episode Count' : {
                                'Current' : 0,
                                'Total' : aniData["episodes"]
                            },
                        'Base Speed' : config.getBaseSpeed(),
                        'Score' : {
                                'Average Score ' : 0,
                                'Scaled Score ' : 0,
                                'NN Score ' : 0,
                                'Real Score ' : 0,
                            },
                        
                        'Episode Length' : aniData['duration']
                        })
            print("here5")

            with open(Path, "w+") as json_file:
                    json.dump(Data, json_file, indent = 4, ensure_ascii = True)
        
        #make list using data from file if file exists
        else:

            #opens file and stores content in json
            with open(Path, "r+") as json_file:
                Data = json.load(json_file)
        
        #gets information from json and stores it to instance
        print("here6")
        self.Data = Data
        self.aniData = aniData
        self.status = status
        self.animeName = animeName
        self.Path = Path
        print("here7")
        self.episodeCurrent = Data['Info']['Episode Count']['Current']
        print("here8")
        self.episodeTotal = Data['Info']['Episode Count']['Total']
        self.baseSpeed = Data['Info']['Base Speed']
        self.avgScore = Data['Info']['Score']['Average Score']
        self.scaledScore = Data['Info']['Score']['Scaled Score']
        self.nnScore = Data['Info']['Score']['nnScore']
        self.realScore = Data['Info']['Score']['Real Score']
        self.speedChangeable = config.getSpeedChangeable()
        print("here8")

        #Shows prompt for user
        userPrompt()
        print("here10")

        #writes to file
        with open(Path, "w+") as json_file:
            json.dump(Data, json_file, indent = 4, ensure_ascii = True)
        pass

    def userPrompt():
        '''prompts user with options on what to do with anime'''
        
        #initializes variables to use in method
        animeName = self.animeName
        print("here9")
        while(true):
            #shows user options
            print("                 " + animeName)
            print("1. Record Watching Stats")
            print("2. Get Watching Stats and Ratings")
            print("3. Other Settings")
            print("x. Go back")
            
            ans = input()

            #takes user to respective methods
            if(int(ans) == 1):
                recordStats()
            
            elif(int(ans) == 2):
                getStats()

            elif(int(ans) == 3):
                Settings()

            elif(ans == "x" or ans == "X"):
                break;
        pass

    def recordStats():
        '''gets and records per episode score and speed from user'''
        
        #initializes variables to use in method
        episodeCurrent = self.episodeCurrent
        episodeTotal = self.episodeTotal
        speedChangeable = self.speedChangeable
        baseSpeed = self.baseSpeed
        animeName = self.animeName
        Data = self.Data

        while(true):
            #asks episode score from user
            print("How do you rate Episode " + episodeCurrent + "of " + animeName + "?")

            epScore = input()
                #retakes and informs user if input is not valid
            while(not epScore.isdigit()):
                print("That is not a valid input. Please enter a number. To exit the program enter -1")
                epScore = input()

                #stops taking in episode scores if input is -1
            if(epScore == -1):
                break;

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

            #updates episode count
            episodeCurrent += 1
            if(episodeTotal > episodeCurrent):
                episodeTotal = episodeCurrent

            #adds score and speed to data
            Data['Episodes'].append({
                        {'Episode ' + epCurrent},
                        {'Score: ' + epScore},
                        {'Speed: ' + epSpeed}
            })

            #updates data list in instance
            self.Data = Data
        
        #updates values in instance
        self.episodeCurrent = episodeCurrent
        self.episodeTotal = episodeTotal

        pass
pass
    

