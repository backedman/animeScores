import pathlib
import requests
import json
import webbrowser
from API.animeList import *
from API.AniListAccess import *



speedChangeable = False
baseSpeed = 1.0


class config(object):
    """files related to the config"""

    #reads config for general info if it exists. If config does not exist, then one is created



    def readConfig():
        global speedChangeable
        global baseSpeed
        global AuthToken
        global AccessCode


        confExists = pathlib.Path("config.txt").exists()
        if confExists:
            with open("config.txt", "r") as config:

                #sets speedChangeable
                lineCont = config.readline()
                if(lineCont.find('True') > -1):
                    speedChangeable = True
                else:
                    speedChangeable = False
        
                #sets baseSpeed
                lineCont = config.readline()
                lineCont = lineCont.replace("baseSpeed: ", "")
                lineCont = lineCont.replace("\n", "")
                if(lineCont.isdecimal):
                    baseSpeed = float(lineCont)
                else:
                    baseSpeed = 1.0

                #sets ANILIST AuthToken
                config.readline()
                lineCont = config.readline()
                lineCont = lineCont.replace("ANILIST AuthToken:", "")
                lineCont = lineCont.replace("\n", "")
                AuthToken = lineCont
                AniListAccess.setAuthToken(AuthToken)

                #sets ANILIST AccessCode
                config.readline()
                lineCont = config.readline()
                lineCont = lineCont.replace("ANILIST AccessCode: ", "")
                lineCont = lineCont.replace("\n", "")
                AccessCode = lineCont
                AccessCode = AniListAccess.setAccessToken(AccessCode)
             
                #sets User ID
                lineCont = config.readline()
                lineCont = lineCont.replace("ANILIST UserID: ", "")
                lineCont = lineCont.replace("\n", "")
                userID = lineCont
                AniListAccess.setUserID(userID)


                pass
        else:
            with open("config.txt", "w+") as config:
                config.write("Enable_Speed_Changes: False\n")
                speedChangeable = False

                config.write("baseSpeed: 1.0\n")
                baseSpeed = 1.0


                #get AniList Auth token to get permission to access user account
                config.write("ANILIST AuthToken: ")
                AuthToken = AniListAccess.findAniListAuthToken()
                config.write(AuthToken)
                config.write("\n")

                #get AniList Access Token to manage user account
                config.write("ANILIST AccessCode: ")
                AccessCode = AniListAccess.findAniListAccessToken(AuthToken)
                config.write(AccessCode)
                config.write("\n")
            
                #get UserID
                config.write("ANILIST UserID: ")
                UserID = AniListAccess.findUserID()
                config.write(UserID)
                config.write("\n")

                config.seek(0)
                print(config.readlines())
                pass
        pass



    #
    #                               GET METHODS BELOW
    #


    def getSpeedChangeable():
        print(speedChangeable)
        return speedChangeable

    def getBaseSpeed():
        return baseSpeed