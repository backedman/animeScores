import json
import os
from API.animeList import *
from Converter.getData import *
from Algorithms.numManip import *

class Converter(object):
    
    def converter():
        Path = "C:/Users/Mohit Bogineni/Desktop/animescores/Data/"
        status = "Watching"
        nStatus = "CURRENT"

        mPath = Path + status
        files = os.listdir(mPath)
        counter = 0
        for x in files:
            aPath = mPath + "/" + x

            x = x.replace(".txt", "")
            print(x)
            aniData = animeList.getAnimeSearch(x)
            print(aniData['title']['romaji'])

            anime = getData.readFile(aPath)
            print("here1")
            Info = anime[0]
            print("here4")


            epData = getData.splitScore(anime[1])

            print("here5")
            print(Info)

            epScore = epData[0]
            epSpeed = epData[1]

            print(Info)
            animeName = Info[0]
            animeName = aniData['title']['romaji']

            print("here2")


            status = Info[1].replace("Status: ", "")

            epCurrent = int(Info[2].replace("Episodes: ", ""))

            baseSpeed = float(Info[3].replace("Base Speed: ", ""))

            scaledScore = float(Info[4].replace("Score: ", ""))

            impactRating = float(Info[5].replace("    Impact Rating: ", ""))
            
            avgScore = float(Info[6].replace("Average Score: ",""))

            #realScore = float(Info[7].replace("Real Score: ", ""))

            print("here3")

            Data = {'Info' : {}, 'Episodes' : {}}


            print(anime)
            Data['Info'] = {'Anime Name' : animeName,
                        'Status' : "CURRENT",
                        'Episode Count' : {
                                'Current' : epCurrent,
                                'Total' : aniData['episodes']
                            },
                        'Base Speed' : baseSpeed,
                        'Score' : {
                                'Average Score' : avgScore,
                                'Scaled Score' : scaledScore,
                                'NN Score' : 0,
                                'Real Score' : 0,
                            },
                        'Impact Rating' : impactRating,
                        'Episode Length' : aniData['duration']
                        }
            print("here8")
            Data['Episodes'] = list()
            for x in range(0, epCurrent):
                dataToAppend = {('Episode ' + str(x + 1)) : {'Score' : str(epScore[x]) , 'Speed' : str(epSpeed[x])}}
                Data['Episodes'].append(dataToAppend)

            print(Data)
            
            
            newPath = mPath + "/" + numManip.makeSafe(animeName) + ".txt"
            os.rename(aPath, newPath)

            with open(newPath, "w+") as json_file:
                json.dump(Data, json_file, indent = 4, ensure_ascii = True)












    pass
Converter.converter()





