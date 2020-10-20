#imports 
import pathlib


def main():
    #initialize variables
    speedChangeable = False
    baseSpeed = 1.0
    AuthToken = ""





    #gets information from config
    readConfig()


#reads config for general info if it exists. If config does not exist, then one is created
def readConfig():
    global speedChangeable
    global baseSpeed
    global AuthToken


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


            pass
    else:
        with open("config.txt", "w+") as config:
            config.write("Enable_Speed_Changes: False\n")
            speedChangeable = False

            config.write("baseSpeed: 1.0\n")
            baseSpeed = 1.0

            config.write("MAL AuthToken: ")
            #get MAL AuthToken
            AuthToken = getMalAuthToken()

            config.seek(0)
            print(config.readlines())
            pass f

def getMALAuthToken():




    return AuthToken

    #pull list from MAL API











main()