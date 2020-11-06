import math

class Search(object):
    """binary search of an array"""

    def bSearchAnimeList(list, target):
        start = 0
        middle = math.floor(len(list)/2)
        end = len(list) - 1
        print(list)

        #search
        while(True):
            middle = (start + end) // 2
            midpoint = list[middle]['media']['title']['userPreferred']
            print(target)
            print(midpoint)
            if(midpoint < target):
                start = middle + 1
                print("start: " + str(start))
            elif(midpoint > target):
                end = middle - 1
                print("end: " + str(end))
            else:
                print("found")
                return middle
            print("middle: " + str(middle))
        pass
