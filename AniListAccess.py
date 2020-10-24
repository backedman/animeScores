import pathlib
import requests
import json
import webbrowser


#sets global variables
CLIENT_ID = "4226"
CLIENT_SECRET = "7wEknYuigwNkGaaXQts4MRmxrMUO4e6YRqry0Ary"
REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"
RESPONSE_TYPE = 'code'
AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize?"
AUTH_TOKEN = ""
ACCESS_URL = "https://anilist.co/api/v2/oauth/token"
QUERY_URL = "https://graphql.anilist.co"
ACCESS_TOKEN = ""
ACCESS_HEADER = ""
USER_ID = ""

"""accesses and authenticates user using AniList API"""
class AniListAccess(object):
    
    #gets Auth token from user
    def getAniListAuthToken():
        global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, RESPONSE_TYPE, AUTHORIZE_URL, AUTH_TOKEN, ACCESS_URL
        
        newAUTHORIZE_URL = AUTHORIZE_URL + "client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&response_type=" + RESPONSE_TYPE
        print(newAUTHORIZE_URL)
        authToken = input("")

        return authToken

    #uses AuthToken to get AccessToken
    def getAniListAccessToken(AuthToken):
        
        global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, RESPONSE_TYPE, AUTHORIZE_URL, AUTH_TOKEN, ACCESS_URL, ACCESS_TOKEN

        AUTH_TOKEN = AuthToken

        #sets data to send to server
        form_params = {
                'grant_type' : 'authorization_code',
                'client_id' : CLIENT_ID,
                'client_secret' : CLIENT_SECRET,
                'redirect_uri' : REDIRECT_URI,
                'code' : AUTH_TOKEN,
                }
        header= {
                'Accept' : 'application/json'
                }
            
            


        #gets accessToken
        accessToken = requests.post(url = ACCESS_URL, json = form_params,  headers = header)
        accessToken = json.loads(accessToken.content)
        accessToken = accessToken['access_token']
        ACCESS_TOKEN = accessToken
        AniListAccess.setAccHead()
                
    pass

     #allows setting ACCESS_TOKEN from a method outside of the class
    def updateAccessToken(accessToken):
        global ACCESS_TOKEN
        ACCESS_TOKEN = accessToken
        AniListAccess.setAccHead()
    pass

    #sets header which sends user access code to the servers
    def setAccHead():
        global ACCESS_TOKEN, ACCESS_HEADER

        ACCESS_HEADER = {
            'Authorization' : 'Bearer ' + ACCESS_TOKEN,
            'Content-Type' : 'application/json',
            'Accept' : 'application/json'
            }
    pass
    
    #finds user ID from server using Access Code
    def getUserID():
        global QUERY_URL, ACCESS_HEADER, USER_ID
        #sets query parameters to request user data
        query = '''
        query {
            Viewer{
                id
            }
        }
        '''

        #Defines variables that will be used in query request
        variables = {
            }

        #get user data from server
        userData = requests.post(QUERY_URL, json = {'query': query, 'variables' : variables}, headers = ACCESS_HEADER)
        
        #gets the user data
        userID = json.loads(userData.content)
        USER_ID = userID["data"]
    pass

    def setUSER_ID(userID):
        global USER_ID
        USER_ID = userID
    pass

    def getAniListAnimeList():
        global USER_ID

    pass

    
        
        
    