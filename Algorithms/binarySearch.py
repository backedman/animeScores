import math

class Search(object):
    """binary search of an array"""

    def bSearchAnimeList(list, target):
        start = 0
        middle = math.floor(len(list)/2)
        end = len(list) - 1

        #search
        while(True):
            middle = (start + end) // 2
            midpoint = list[middle]['title']['romaji']
            print(target)
            print(midpoint)
            if(target > midpoint):
                start = middle -1
            elif(target < midpoint):
                end = middle - 1
            elif(target == midpoint):
                print("found")
                return list[middle]
        pass
