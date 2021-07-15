import math
import os

class valManip(object):
    '''class that allows for manipulation of numbers sent through'''

    def round(num, digit):
        '''gets rounded number based on given siginificant digit and number'''
        
        #calculates rounded number
        digitMulti = math.pow(10, digit)
        try:
            roundedNum = (int)(num * digitMulti + 0.5)/(digitMulti)
        except:
            return None

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

    def getPath(stat=None):
        if(stat==None):
            Path = os.getcwd() + "/Data/"
        else:
            Path = os.getcwd() + "/Data/" + stat + "/"
        os.makedirs(Path, exist_ok=True)

        return Path

    def sqrtKeepNeg(value):
        '''returns the square root of a number while keeping the negative'''

        if(value >= 0):
            return math.sqrt(value)
        else:
            return -math.sqrt(abs(value))