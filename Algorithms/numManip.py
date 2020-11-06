import math

class numManip(object):
    '''class that allows for manipulation of numbers sent through'''

    def round(num, digit):
        '''gets rounded number based on given siginificant digit and number'''
        
        #calculates rounded number
        digitMulti = math.pow(10, digit)
        roundedNum = int((num * digitMulti + 0.5))/(digitMulti)

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
        name = numManip.makeSafe(name)

        name = name.replace("'", "");
        name = name.replace(".","");
        name = name.replace("…","");

        return name

