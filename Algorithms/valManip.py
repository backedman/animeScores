import math
import os

class valManip(object):
    '''class that allows for manipulation of numbers sent through'''

    def round(num, digit):
        '''gets rounded number based on given siginificant digit and number'''
        
        #calculates rounded number
        digitMulti = math.pow(10, digit)
        roundedNum = (int)(num * digitMulti + 0.5)/(digitMulti)

        return roundedNum

    def makeSafe(name):
        name = name.replace("?", " ")
        name = name.replace("!", " ")
        name = name.replace("<", " ")
        name = name.replace(">", " ")
        name = name.replace("\"", " ")
        name = name.replace("/", " ")
        name = name.replace("\\", " ")
        name = name.replace("|", " ")
        name = name.replace("*", " ")
        name = name.replace(":", " ")

        return name

    def makeCompareable(name):

        name = valManip.makeSafe(name)

        name = name.replace("'", "");
        name = name.replace(".","");
        name = name.replace("…","");

        return name

    def getPath(stat):
        Path = os.getcwd() + "/Data/" + stat + "/"
        os.makedirs(Path, exist_ok=True)

        return Path
