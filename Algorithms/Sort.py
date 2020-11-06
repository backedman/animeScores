import math
import sys

class Sort(object):
    '''various sort methods for arrays'''

    def qSort(animeList):
        '''quick sort anime List. Code taken from geeksforgeeks.org/python-program-for-quicksort/'''
        
        if len(animeList) == 0:
            return False

        aniList = animeList['entries']

        #sets low and high variables
        low = 0;
        high = len(aniList) - 1


        #title Case list
        aniList = Sort.titleCaseAniList(aniList)


        pi = 0

        if (low < high):
            # pi is partitioning index, aniList[p] is now at right place
            pi = Sort.qPartition(aniList, low, high);

            Sort.qSortCont(aniList, low, pi - 1);  #Before pi
            Sort.qSortCont(aniList, pi + 1, high); #After pi

        animeList['entries'] = aniList


    def qSortCont(aniList, low, high):
        '''quick sort anime List but accepts low and high values. Code taken from geeksforgeeks.org/python-program-for-quicksort/'''

        pi = 0

        if (low < high):
            # pi is partitioning index, aniList[p] is now at right place 
            pi = Sort.qPartition(aniList, low, high);

            Sort.qSortCont(aniList, low, pi - 1);  #Before pi
            Sort.qSortCont(aniList, pi + 1, high); #After pi


    def qPartition(aniList, low, high):
        '''partition method for quick sort. Code taken from geeksforgeeks.org/python-program-for-quicksort/'''



        i = (low-1)         # index of smaller element
        pivot = aniList[high]['media']['title']['userPreferred']     # pivot

        

        for j in range(low, high):
 
            # If current element is smaller than or
            # equal to pivot
            if aniList[j]['media']["title"]["userPreferred"] <= pivot:
 
                # increment index of smaller element
                i = i+1
                aniList[i], aniList[j] = aniList[j], aniList[i]
 
        aniList[i+1], aniList[high] = aniList[high], aniList[i+1]
        return (i+1)

    def titleCaseAniList(aniList):
        '''returnes titleCased version of list'''

        length = len(aniList)

        for x in range(0, length): #x is the index for the given anime list. Each index corresponds with a different anime
            aniList[x]['media']['title']['userPreferred'] = aniList[x]['media']['title']['userPreferred'].title()

        return aniList
    
