#imports 
import pathlib
import requests
import json
import webbrowser
from AniListAccess import *

def main():
    #initialize variables
    speedChangeable = False
    baseSpeed = 1.0
    AuthToken = ""
    AccessCode = ""





    #gets information from config
    readConfig()

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
            if(lineCont.find('True')):
                speedChangeable = True
            else:
                speedChangeable = False
        
            #sets baseSpeed
            lineCont = config.readline()
            lineCont = lineCont.replace("baseSpeed: ", "")
            lineCont = lineCont.replace("\n", "")
            print(lineCont)
            if(lineCont.isdecimal):
                baseSpeed = float(lineCont)
            else:
                baseSpeed = 1.0

            #sets MAL AuthToken
            lineCont = config.readline()
            lineCont = lineCont.replace("MAL AuthToken: ", "")
            lineCont = lineCont.replace("\n", "")
            AuthToken = lineCont

            #sets ANILIST AccessCode
            lineCont = config.readline()
            lineCont = lineCont.replace("ANILIST AccessCode: ", "")
            lineCont = lineCont.replace("\n", "")
            AccessCode = lineCont


            pass
    else:
        with open("config.txt", "w+") as config:
            config.write("Enable_Speed_Changes: False\n")
            speedChangeable = False

            config.write("baseSpeed: 1.0\n")
            baseSpeed = 1.0


            #get AniList Auth token to get permission to access user account
            config.write("ANILIST AuthToken: ")
            AuthToken = AniListAccess.getAniListAuthToken()
            config.write(AuthToken)

            #get AniList Access Token to manage user account
            config.write("ANILIST AccessCode: ")
            AccessCode = AniListAccess.getAniListAccessToken(AuthToken)
            config.write(AccessCode)
            


            config.seek(0)
            print(config.readlines())
            pass










main()