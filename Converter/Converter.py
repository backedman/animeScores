import json
import os
from API.animeList import *
from Converter.getData import *
class Converter(object):
    
    def converter():
        Path = "C:/Users/Mohit Bogineni/Desktop/animescores/Data/"
        status = "Completed"
        nStatus = "COMPLETED"

        mPath = Path + status
        files = os.listdir(mPath)

        for x in files:
            aPath = mPath + "/" + x

            x = x.replace(".txt", "")
            anime = animeList.getAnimeSearch(x)
            
            getData.readFile(aPath)
                


            break










    pass
Converter.converter()





