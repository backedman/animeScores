import pathlib
import requests
import json
import webbrowser
import os
import threading
from AniListAPI.AniListAccess import *
from AniListAPI.updateAnime import *
from AniListAPI.animeList import *
from Algorithms.Search import *
from Algorithms.recommendations import *
from anime.animeFile import *
from runnables.config import *
from neuralNetwork.recNeuralNet import *
from neuralNetwork.neuralNet import *

def main():
   #initialize variables
    speedChangeable = False
    baseSpeed = 1.0
    AuthToken = ""
    AccessCode = ""
    status = "CURRENT"


   #updates or creates information from config
    config.readConfig()
    speedChangeable = config.getSpeedChangeable()
    baseSpeed = config.getBaseSpeed()

   
    

  #gets the most up to date user's anime list from website
    aniList = animeList.updateAniListAnimeList()
    animeList.updateFiles()
    titleList = animeList.getTitleList(status)
        

    #initializes neuralNetwork
    neuralNet.initialize()

    # set current page number and maximum page number (each page has 9)
    page = 1

    # program continues until user wants to exit
    while (True):
        addSpacing()

        maxPage = int((len(titleList) / 9 + 1.5))


        print("Page " + str(page) + "/" + str(maxPage))
        # shows anime in page
        for x in range(1, 10):
            if (x <= len(titleList) - (page - 1) * 9):
                listIndex = x - 1 + (page - 1) * 9
                listAnime = titleList[listIndex]
                print(str(x) + "." + str(listAnime))

        # gets user input
        print("         ")
        print("N. Manual/New ")
        print("Q. Previous Page ")
        print("E. Next Page")
        print("A. Choose Page")
        print("S. Search")
        print("F. Find Reccomendation")
        print("O. Options")
        print("X. Exit Program ")
        ans = input()
        print("\n\n\n\n\n\n\n\n\n\n")

        # searches for anime from api and makes it a file
        if (ans == "N" or ans == "n"):
            print("Name of anime?")
            anime = input()
            animeName = animeList.getAnimeSearch(anime)['title']['userPreferred']
            aniShow = animeFile(animeName, status)

        # goes back a page if user chooses "Q"
        elif (ans == "Q" or ans == "q"):
            page -= 1

        # goes forward a page if user chooses "E"
        elif (ans == "E" or ans == "e"):
            page += 1

        # goes to user specified page
        elif (ans == "A" or ans == "a"):
            page = int(input())

        elif (ans == "S" or ans == "s"):
            print("Name of anime to search")
            animeName = input()
            listResults = animeList.getAnimeSearchList(animeName, 5)['media']

            sPage = 1
            sMaxPage = int(len(listResults) / 9 + 1.5)

            # shows anime search results in a list user can choose options from
            while (True):

                print("Page " + str(sPage) + "/" + str(sMaxPage))
                for x in range(1, 10):
                    if (x <= len(listResults) - (sPage - 1) * 9):
                        listIndex = x - 1 + (sPage - 1) * 9
                        listAnime = listResults[listIndex]['title']['userPreferred']
                        print(str(x) + "." + str(listAnime))
                print("Q. Previous Page ")
                print("E. Next Page")
                print("A. Choose Page")
                print("X. Go back")
                print("\n\n\n\n\n\n\n\n\n\n")

                ans = str(input())

                # goes back a page if user chooses "Q"
                if (ans == "Q" or ans == "q"):
                    sPage -= 1

                # goes forward a page if user chooses "E"
                elif (ans == "E" or ans == "e"):
                    sPage += 1

                # goes to user specified page
                elif (ans == "A" or ans == "a"):
                    sPage = int(input())

                # selects choice based on user input
                elif (ans == "x" or ans == "X"):
                    break;

                elif (int(ans) < 10 and int(ans) > 0):
                    listIndex = int(ans) - 1 + (sPage - 1) * 9
                    animeName = listResults[listIndex]['title']['userPreferred']

                    aniShow = animeFile(animeName, status)

        elif (ans == "F" or ans == "f"):
            print("1. Normal")
            print("2. Experimental (not recommended)")

            ans = input()

            if(ans == "1"):
                titleList = recommendations.findReccomendedLegacy()
            elif(ans == "2"):
                titleList = recommendations.findReccomended()
           


        # opens options menu
        elif (ans == "O" or ans == "o"):
            
            # asks user for input
            print("1. Open another list")
            print("2. Mass update scores")
            print("3. Neural Network")
            print("4. predict score of anime (using the recommendations algorithm)")

            ans = int(input())

            if(ans == 1): #user changes between different list types (current, completed, planning, etc.)

                # asks user for input
                print("1. Open WATCHING list")
                print("2. Open COMPLETED list")
                print("3. Open PLANNING list")
                print("4. Open PAUSED list")
                print("5. Open DROPPED list")
                print("6. Open ALL list")
                ans = int(input())

                # switches list if user chooses corresponding option
                if(ans == 1):
                    status = "CURRENT"
                elif(ans == 2):
                    status = "COMPLETED"
                elif(ans == 3):
                    status = "PLANNING"
                elif(ans == 4):
                    status = "PAUSED"
                elif(ans == 5):
                    status = "DROPPED"
                elif(ans == 6):
                    status = "ALL"

                # updates list and pages
                titleList = animeList.getTitleList(status)
                page = 1
                maxPage = int((len(titleList) / 9 + 1.5))

            elif(ans == 2):

                updateAnime.massUpdateNNScore()
                updateAnime.massUpdateScore()

            elif(ans == 3):

                print("1. run with Impact Rating")
                print("2. run without Impact Rating")
                print("3. run Both with and without (recommended)")

                ans = int(input())

                runImpact = False
                runWithout = False

                #sets conditional for if the neural network should access impact nn, no impact nn, or both
                if(ans == 1):
                    runImpact = True

                elif(ans == 2):
                    runWithout = True

                elif(ans == 3):
                    runImpact = True
                    runWithout = True
                
                    #provides user with options on how to interact with nn
                if(ans == 1 or ans == 2 or ans == 3):
                    print("1. run for 1000 iterations")
                    print("2. run for 10000 iterations")
                    print("3. run for a custom amount of iterations")
                    print("4. recalculate (starts from scratch)")
                    print("5. manually test neural network")
                    print("X. back")

                    ans = int(input())

                    if(ans == 1):
                        iterations = 1000
                        cont = True #runs nn from where it left off before

                    elif(ans == 2):
                        iterations = 10000
                        cont = True

                    elif(ans == 3):
                        print("How many iterations?")
                        iterations = int(input())
                        cont = True

                    elif(ans == 4):
                        iterations = 10000
                        cont = False #starts nn from scratch

                    elif(ans == 5): #user enters values manually to see how it impacts nn. For transperency and testing purposes
                        while(True):
                            print("ep Count")
                            epCount = int(input())
                            print("avg Score")
                            avgScore = float(input())
                            print("impactScore")
                            impactScore = float(input())
                            print("speed dev")
                            baseSpeedDev = float(input())
                            print("ep Dev")
                            epScoreDev = float(input())

                            if(runImpact):
                                stats = numpy.array([epCount, avgScore, impactScore, baseSpeedDev, epScoreDev])
                                stats = numpy.reshape(stats, (-1, 5))
                                prediction = neuralNet.predict(stats)

                                print("nnScore: " + str(prediction))

                            if(runWithout):
                                stats = numpy.array([epCount, avgScore, baseSpeedDev, epScoreDev])
                                stats = numpy.reshape(stats, (-1, 4))
                                print("here")
                                prediction = neuralNet.predictNoImpact(stats)

                                print("nnScorenoImpact: " + str(prediction))

                            print("press x to leave. Press any other button to continue")
                            if(input() == "x"):
                                break

                    if(runImpact):
                        neuralNet.train(iterations, cont)
                    if(runWithout):
                        neuralNet.trainNoImpact(iterations, cont)
              


            elif(ans == 4):
                 
                 nnRec = recNeuralNet()
                 
                 while (True):
                    
                    #allows user to search for anime based on input
                    addSpacing()
                    print("Name of anime to search")
                    animeSearch = input()
                    listResults = animeList.getAnimeSearchList(animeSearch, 10)['media']

                    sPage = 1
                    sMaxPage = int(len(listResults) / 9 + 1.5)

                    #shows anime results from search
                    print("Page " + str(sPage) + "/" + str(sMaxPage))
                    for x in range(1, 10):
                        if (x <= len(listResults) - (sPage - 1) * 9):
                            listIndex = x - 1 + (sPage - 1) * 9
                            listAnime = listResults[listIndex]['title']['userPreferred']
                            print(str(x) + "." + str(listAnime))

                    ans = str(input()) #gets user input

                    listIndex = int(ans) - 1 + (sPage - 1) * 9
                    animeName = listResults[listIndex]['title']['userPreferred']

                    anime = animeList.getAnimeDetailed(animeName) #gets detailed information from the anime the user chose

                    print(anime)

                    genres = anime['genres']
                    tags = anime['tags']
                    tagRank = [0] * len(tags)

                    for x in range(len(tags)): #assigns ranks from the API to the tags, as well as remove the "name" modifier from the tags to make it compareable to the genre list
                        tagRank[x] = tags[x]['rank']
                        tags[x] = tags[x]['name']
                

                    genreTagBinary = findGenreTagBinary(genres, tags, tagRank) #gets the binary representation for the genres and tags
                    averageScore = anime['averageScore']

                    animeValue = nnRec.predict(genreTagBinary, averageScore) #predicts score of anime

                    print(animeName + ": " + str(animeValue)) #prints score of anime to user





        # exits program if user chooses "X"
        elif (ans == "x" or ans == "X"):
                break

        # chooses corresponding animeName if user chooses a number between 1 and 9
        elif (int(ans) < 10 and int(ans) > 0):
            listIndex = int(ans) - 1 + (page - 1) * 9
            animeName = titleList[listIndex]

            aniShow = animeFile(animeName, status)
            
        pass

def addSpacing():
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")
    print("       ")




if __name__ == '__main__':
    mainThread = threading.Thread(target = main())

    mainThread.start() 