import math
import os

class valManip(object):
    '''class that allows for manipulation of numbers sent through'''

    def round(num, digit):
        '''gets rounded number based on given siginificant digit and number'''
        
        if(num == None):
            return 0

        #calculates rounded number
        digitMulti = math.pow(10, digit)
        try:
            roundedNum = (int)(num * digitMulti + 0.5)/(digitMulti)
        except:
            roundedNum = 0
            print("DIVISION BY 0 IN valManip:round")

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
        name = valManip.upperLower(name)

        name = name.replace("'", " ")
        name = name.replace("."," ")
        name = name.replace("…"," ")

        return name

    def upperLower(name):

        name = name.upper()
        name = name.lower()

        return name


    def getPath(stat=None):
        if(stat==None):
            Path = os.getcwd() + "/Data/"
        else:
            Path = os.getcwd() + "/Data/" + stat + "/"

        if(os.path.exists(Path) == False):
            print("Path does not exist")
            print(Path)
            os.makedirs(Path, exist_ok=True)
        return Path

    def sqrtKeepNeg(value):
        '''returns the square root of a number while keeping the negative'''

        if(value >= 0):
            return math.sqrt(value)
        else:
            return -math.sqrt(abs(value))

    def powKeepNeg(value, power=2):
        if(value >= 0):
            return math.pow(value,power)
        else:
            return -math.pow(abs(value),power)