#imports 
import pathlib
import requests
import json
import webbrowser
import os
from API.AniListAccess import *
from API.animeList import *
from config import *
from anime.animeFile import *
from Algorithms.binarySearch import *



def main():
    #initialize variables
    speedChangeable = False
    baseSpeed = 1.0
    AuthToken = ""
    AccessCode = ""
    status = "PLANNING"




    #updates or creates information from config
    config.readConfig()
    speedChangeable = config.getSpeedChangeable()
    baseSpeed = config.getBaseSpeed()


    #gets the most up to date user's anime list from website
    aniList = animeList.updateAniListAnimeList("PLANNING")
    titleList = animeList.getTitleList("PLANNING")


    #set current page number and maximum page number (each page has 9)
    maxPage = int((len(titleList)/9 + 1.5))
    page = 1

    #program continues until user wants to exit
    while(True):
        print("Page " + str(page) + "/" + str(maxPage))
            #shows anime in page
        for x in range(1, 10):
            if(x < len(titleList) - (page - 1) * 9):
                print(str(x) + "." + str(titleList[x - 1 + (page - 1) * 9]))
        
        #gets user input
        print("N. Manual/New ")
        print("Q. Previous Page ")
        print("E. Next Page")
        print("A. Choose Page")
        print("O. Options")
        print("X. Exit Program ")
        ans = input()
        
        #searches for anime or picks anime in list if it already exists if user chooses "N"
        if(ans == "N" or ans == "n"):
            nothingHappens = True

        #goes back a page if user chooses "Q"
        elif(ans == "Q" or ans == "q"):
            page -= 1
        
        #goes forward a page if user chooses "E"
        elif(ans == "E" or ans == "e"):
            page += 1
        
        #goes to user specified page
        elif(ans == "A" or ans == "a"):
            page = int(input())

        #opens options menu
        elif(ans == "O" or ans == "o"):
            #asks user for input
            print("1. Open PLANNING list")
            print("2. Open WATCHING list")
            print("3. Open COMPLETED list")
            print("4. Open ALL list")
            ans = int(input())

            #switches list if user chooses corresponding option
            if(ans == 1):
                status = "PLANNING"
            elif(ans == 2):
                status = "CURRENT"
            elif(ans == 3):
                status = "COMPLETED"
            elif(ans == 4):
                status = "all"
            
            #updates list and pages
            titleList = animeList.getTitleList(status)
            page = 1
            maxPage = int((len(titleList)/9 + 1.5))



        #exits program if user chooses "X"
        elif(ans == "x" or ans == "X"):
            break

        #chooses corresponding animeName if user chooses a number between 1 and 9
        elif(int(ans) < 10 and int(ans) > 0):
            animeName = str(titleList[int(ans) - 1 + (page - 1) * 9])
            
            print("here")
            aniShow = animeFile(animeName, status)
            #checks if file for anime exists. If it doesn't, then a new one is created
            animePath = getPath(status) + animeName + ".txt"
            animeExists = pathlib.Path(animePath)

    pass
            


            
            




def getPath(stat):
    Path = os.getcwd() + "/Data/" + stat + "/"
    os.makedirs(Path, exist_ok = True)

    return Path
    pass
pass

if __name__ == '__main__':
    main()








