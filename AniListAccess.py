import pathlib
import requests
import json
import webbrowser

class AniListAccess(object):
    """accesses and authenticates user using AniList API"""

    #sets global variables
    CLIENT_ID = "4226"
    CLIENT_SECRET = "7wEknYuigwNkGaaXQts4MRmxrMUO4e6YRqry0Ary"
    REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"
    RESPONSE_TYPE = 'code'
    AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize?"
    AUTH_TOKEN = ""
    ACCESS_URL = "https://anilist.co/api/v2/oauth/token"


    #gets Auth token from user
    def getAniListAuthToken():
        CLIENT_ID = "4226"
        CLIENT_SECRET = "7wEknYuigwNkGaaXQts4MRmxrMUO4e6YRqry0Ary"
        REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"
        RESPONSE_TYPE = 'code'
        AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize?"
        AUTH_TOKEN = ""
        ACCESS_URL = "https://anilist.co/api/v2/oauth/token"
        
        newAUTHORIZE_URL = AUTHORIZE_URL + "client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&response_type=" + RESPONSE_TYPE
        print(newAUTHORIZE_URL)
        authToken = input("")

        return authToken

    #uses AuthToken to get AccessToken
    def getAniListAccessToken(AuthToken):

        CLIENT_ID = "4226"
        CLIENT_SECRET = "7wEknYuigwNkGaaXQts4MRmxrMUO4e6YRqry0Ary"
        REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"
        RESPONSE_TYPE = 'code'
        AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize?"
        AUTH_TOKEN = ""
        ACCESS_URL = "https://anilist.co/api/v2/oauth/token"
        AUTH_TOKEN = AuthToken

       
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
            
            
        print(AUTH_TOKEN)



        accessToken = requests.post(url = ACCESS_URL, json = form_params,  headers = header)
        accessToken = json.loads(accessToken.content)
        accessToken = accessToken['access_token']
        print(accessToken)
        
    pass


