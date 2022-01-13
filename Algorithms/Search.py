import math
from Algorithms.valManip import *

class Search(object):
    """binary search of an array"""

    def bSearchAnimeList(list, animeName=None, anime_id=None):

        if(animeName is not None):
            
            target = valManip.makeCompareable(animeName)
            

            return Search.linearSearch(list, animeName=target)

        elif(anime_id is not None):

            start = 0
            middle = math.floor(len(list['entries'])/2)
            end = len(list['entries']) - 1
            counter = 0

            target = anime_id

            while(True):
                middle = (start + end) // 2
                midpoint = list['entries'][middle]['media']['id']

                if(midpoint < target):
                    start = middle + 1
                elif(midpoint > target):
                    end = middle - 1
                else:
                    return middle
                counter += 1

                if(counter >= len(list['entries'])): #performs a linear search if binary search is not working
                    return Search.linearSearch(list, anime_id=target)

        pass

    def linearSearch(list, animeName=None, anime_id=None):
       
       listLen = len(list['entries'])

       if(animeName is not None):

           for x in range(0, listLen):
               listVal = list['entries'][x]['media']['title']['userPreferred']

               if(valManip.makeCompareable(listVal) == valManip.makeCompareable(animeName)): #returns index if value is found
                 #print("OMG THE BINARY SEARCH BROKE!!!")
                 return list['entries'][x]

       elif(anime_id is not None):
           
           for x in range(0, listLen):
               listVal = list['entries'][x]['media']['id']

               if(listVal == anime_id): #returns index if value is found
                 #print("OMG THE BINARY SEARCH BROKE!!!")
                 return list['entries'][x]
       
       return None
