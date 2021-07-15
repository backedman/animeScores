import math
from Algorithms.valManip import *

class Search(object):
    """binary search of an array"""

    def bSearchAnimeList(list, target):
        start = 0
        middle = math.floor(len(list['entries'])/2)
        end = len(list['entries']) - 1
        target = valManip.makeCompareable(target)
        

        #search
        counter = 0
        while(True):
            middle = (start + end) // 2
            midpoint = valManip.makeCompareable(list['entries'][middle]['media']['title']['userPreferred'])

            if(midpoint < target):
                start = middle + 1
            elif(midpoint > target):
                end = middle - 1
            else:
                return middle
            counter += 1

            if(counter >= len(list['entries'])*2): #performs a linear search if binary search is not working
                return Search.linearSearch(list, target)
        pass

    def linearSearch(list, target):
       
       listLen = len(list['entries'])
       for x in range(0, listLen):
           listVal = list['entries'][x]['media']['title']['userPreferred']

           if(valManip.makeCompareable(listVal) == valManip.makeCompareable(target)): #returns index if value is found
             #print("OMG THE BINARY SEARCH BROKE!!!")
             return x

       return -1
