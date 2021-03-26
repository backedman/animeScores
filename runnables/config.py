import pathlib
import requests
import json
import webbrowser
import sys
from AniListAPI.animeList import *
from AniListAPI.AniListAccess import *



speedChangeable = False
baseSpeed = 1.0


class config(object):
    """files related to the config"""

    #reads config for general info if it exists. If config does not exist, then one is created



    def readConfig():
        global speedChangeable
        global baseSpeed
        global userID
        global AuthToken
        global AccessCode
        global prefScr


        confExists = pathlib.Path("config.txt").exists()
        if confExists:
            with open("config.txt", "r+") as file:


                #sets speedChangeable
                lineCont = file.readline()
                if(lineCont.find('True') > -1):
                    speedChangeable = True
                else:
                    speedChangeable = False
                


                #sets baseSpeed
                baseSpeed = file.readline()
                baseSpeed = baseSpeed.replace("baseSpeed: ", "")
                baseSpeed = baseSpeed.replace("\n", "")
                if(baseSpeed.isdecimal):
                    baseSpeed = float(baseSpeed)
                else:
                    baseSpeed = 1.0


                
                #sets User ID
                userID = file.readline()

                userID = userID.replace("ANILIST UserID: ", "")
                userID = userID.replace("\n", "")

                AniListAccess.setUserID(userID)
                



                #sets ANILIST AuthToken
                AuthToken = file.readline()

                AuthToken = AuthToken.replace("ANILIST AuthToken:", "")
                AuthToken = AuthToken.replace("\n", "")
                AuthToken = AuthToken.replace(" ", "")

                AniListAccess.setAuthToken(AuthToken)



                #sets ANILIST AccessCode
                AccessCode = file.readline()
                
                    #takes only the values from the line
                AccessCode = AccessCode.replace("ANILIST AccessCode: ", "")
                AccessCode = AccessCode.replace("\n", "")

                if(AccessCode == ""): #if the line is empty, then part 2 of config creation starts. If its not, then the configs values are pulled
                    
                    AccessCode = AniListAccess.findAniListAccessToken(AuthToken) #finds accessToken
                    userID = AniListAccess.findUserID()

                    config.rewriteConfig()

                else:
                    AniListAccess.setAccessToken(AccessCode)

                prefScr = file.readline()
                prefScr = prefScr.replace("Preferred Score Saving(avg, scaled, real, nn): ", "")
                prefScr = prefScr.replace("\n", "")


                #if userId is blank for some reason, then it is attempted to be found again
                if(userID == "None"):
                    userID = AniListAccess.findUserID()
                    
                    config.rewriteConfig()
                
                if(prefScr == ""):
                    prefScr = "real"
                    config.rewriteConfig()


                pass
        else:
            with open("config.txt", "w+") as file:
                file.write("Enable_Speed_Changes: False\n")
                speedChangeable = False

                file.write("baseSpeed: 1.0\n")
                baseSpeed = 1.0

                #get UserID
                file.write("ANILIST UserID: ")
                file.write("\n")

                #get AniList Auth token to get permission to access user account
                file.write("ANILIST AuthToken: ")
                AniListAccess.findAniListAuthToken()
                print("Log into the link above and copy the code into the 'Auth Token' section of the config file")
                file.write("\n")

                #get AniList Access Token to manage user account
                file.write("ANILIST AccessCode: ")
                file.write("\n")

                file.write("Preferred Score Saving(avg, scaled, real, nn): nn")

                file.seek(0)

                input("Press Enter to Exit")

                sys.exit()

                pass
        pass

    def rewriteConfig():
        global speedChangeable
        global baseSpeed
        global userID
        global AuthToken
        global AccessCode
        global prefScr

        with open("config.txt", "w+") as file:

            file.write("Enable_Speed_Changes: " + str(speedChangeable) + "\n")
            file.write("baseSpeed: " + str(baseSpeed) + "\n")
            file.write("ANILIST UserID: " + str(AniListAccess.getUserID()) + "\n")
            file.write("ANILIST AuthToken: " + str(AuthToken) + "\n")
            file.write("ANILIST AccessCode: " + str(AccessCode) + "\n")
            file.write("Preferred Score Saving(avg, scaled, real, nn): " + str(prefScr) + "\n")

        pass



    #
    #                               GET METHODS BELOW
    #


    def getSpeedChangeable():
        return speedChangeable

    def getBaseSpeed():
        return baseSpeed

    def getPrefScr():
        global prefScr

        if(prefScr == "avg"):
            return "Average Score"
        elif(prefScr == "scaled"):
            return "Scaled Score"
        elif(prefScr == "real"):
            return "Real Score"
        elif(prefScr == "nn"):
            return "NN Score"