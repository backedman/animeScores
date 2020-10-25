#imports 
import pathlib
import requests
import json
import webbrowser
from AniListAccess import *
from animeList import *
from config import *

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
    animeList.updateAniListAnimeList("PLANNING")
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

        #exits program if user chooses "X"
        elif(ans == "x" or ans == "X"):
            break

        #chooses corresponding animeName if user chooses a number between 1 and 9
        elif(int(ans) < 10 and int(ans) > 0):
            animeName = titleList[int(ans) - 1 + (page - 1) * 9]
            print(animeName)



    












main()