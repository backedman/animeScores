from AniListAPI.AniListAccess import *
from Algorithms.valManip import *
from datetime import date


class AniListCalls():

    def getAnimeDetailed(animeName):
        '''gets detailed list of anime'''

        #sets query and variables to get anime from API
        query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    id
                    title{
                        userPreferred
                    }
                    tags{
                        name
                        rank
                    }
                    episodes
                    genres
                    duration
                    averageScore
                    meanScore
                    favourites
				    recommendations{
					    edges{
						    node{
                                rating
							    mediaRecommendation{
								    title{
									    userPreferred
								    }
							    }
						    }
					    }
				    }
                }
            }
            '''
        variables = {
            'animeName' : animeName
        }



        #returns json data of anime
        animeData = (AniListAccess.getData(query, variables))['data']['Media']

        return animeData

    def retAnimeListDet(user="", sort="MEDIA_ID"):

        if(user == ""):
            userName = AniListAccess.getUserName()
        else:
            userName = user

        if(sort is None):
            sort = "MEDIA_ID"

        #sets query to send to server.  This one asks for total number of
        #pages, total anime, name of the anime in a page, and what list the
        #anime is in
        query = '''
        query ($userName: String, $sortType: [MediaListSort])  {
                MediaListCollection(userName : $userName,  type: ANIME, sort: $sortType) {
                    
                     lists {
                          
                          status

                          entries {

                            mediaId
                            media {
                              title{
                                userPreferred
                              }

                              genres

                              tags{
                                name
                                rank
                                category
                              }

                              averageScore
                              popularity

                              mediaListEntry {
                                score
                              }

                              recommendations{
                                edges{
                                    node{
                                        rating
                                        mediaRecommendation{
                                            title{
                                                userPreferred
                                            }
                                        }
                                    }
                        }
                    }

                            }

                          }
            }
                }
        }
        '''
        
        #sets correct information for the query.  If all anime in the list are
        #wanted, then status is not set
        variables = {
            'userName' : userName,
            'sortType' : sort
        }

        #requests data from API into a list
        animeListData = AniListAccess.getData(query, variables)['data']['MediaListCollection']['lists']

        return animeListData

    def getAnimeSearch(animeName):
        '''gets first search result of anime search'''
        query = '''
            query($animeName : String) {
                Media(search : $animeName, type: ANIME)
                {
                    title{
                        userPreferred
                    }
                    id
                    episodes                  
                    duration

                }
            }
            '''
        variables = {
            'animeName' : animeName
        }
        
            #returns data of anime
        
        animeData = (AniListAccess.getData(query, variables))['data']['Media']
        return animeData

    def getAnimeSearchList(animeName, numResults):
        '''gets multiple search results'''
        
        query = '''
            query ($animeName: String, $perPage: Int)  {
            Page(perPage : $perPage){
  	                media(search : $animeName, type : ANIME)
                    {
                        title{
                            userPreferred
                        }
                        episodes                  
                        duration
                    }
                }
            }
        '''
        variables = {
                'animeName' : animeName,
                'perPage' : numResults
            }

        #returns anime results list
        queryData = (AniListAccess.getData(query,variables))['data']['Page']['media']
        
        animeData = []

        for anime in queryData:
            animeTitle = anime['title']['userPreferred']
            animeData.append(animeTitle)

        return animeData

    def getAllAnime(remNonPTW=False):
        '''gets all the anime that's ever been released'''
        global animeListAll

        Path = valManip.getPath() + "data.txt" #creates path to store the list of all anime 

        if(os.path.exists(Path)): #accesses data in file if the file exists and returns it, if the file does not exist, the data is scraped from the api
            with open(Path, "r+") as json_file:
                animeData = json.load(json_file)

            if(remNonPTW == True): #iterates through each anime in the database and removes the ones that are already in the list and completed/dropped

                index = 0

                while(index < len(animeData)):
                    anime = animeData[index]
                    if(anime['mediaListEntry'] != None):
                        status = anime['mediaListEntry']['status']
                        if(status == "COMPLETED" or status == "DROPPED" or status == "CURRENT"):
                            animeData.pop(index)
                            index -= 1
                    index += 1

            return animeData

        query = '''
            {
                '''
        variables = {
            }

        item = 0
        animeData = []
        for year in range(1940, date.today().year + 1): #accesses all anime from 1940 to present day
            for page in range(1,13): #12 pages for each year (600 anime per year)
                query += (''' item%d: Page(page: %d) { 
                                media(type: ANIME, seasonYear: %d){ 
                                    title{ 
                                        userPreferred
                                    }
                                    recommendations{
						                edges{
						                    node{
                                                rating
							                    mediaRecommendation{
								                    title{
									                    userPreferred
								                    }
							                    }
						                    }
						                }
					                }
                                    tags{
                                        name
                                        rank
                                    }
                                    genres

                                    popularity
                                    averageScore

                                    mediaListEntry {
                                        status
                                    }
                                }

                                
                            }

                           ''' % (item, page, year))
                item += 1

            if((date.today().year - year)%2 == 0): #queries the data in 2 year increments (API's call limit only allows for 2 years due to the amount of information we pull)
                query += "}"
                item = 0

                queryData = (AniListAccess.getData(query,variables))['data']

                for x in range(0, len(queryData)): #adds the data from each page into the full database
                    itemstring = 'item%d' % x
                    pageData = queryData[itemstring]['media']

                    if(pageData == []):
                        continue

                    animeData += pageData


                query = '''
                    {
                    '''

        
        with open(Path, "w+") as json_file: #saves data to file
            json.dump(animeData, json_file, indent = 4, ensure_ascii = True)
            json_file.seek(0)

        
        if(remNonPTW == True): #iterates through each anime in the database and removes the ones that are already in the list and completed/dropped

            index = 0

            while(index < len(animeData)):
                anime = animeData[index]
                if(anime['mediaListEntry'] != None):
                    status = anime['mediaListEntry']['status']
                    if(status != "PLANNING" and status != "PAUSED" and status != "CURRENT"):
                        animeData.pop(index)
                        index -= 1
                index += 1

        return animeData #returns data 

    def getAllGenreTags():
        '''returns all possible genres and tags available on anilist. Index 0 contains genres and Index 1 contains tags'''
        global genreTags

        query = '''
            {
                GenreCollection
                MediaTagCollection{
                    name
                }
            }
        '''

        variables = {
            }

        #returns anime results list
        animeData = (AniListAccess.getData(query,variables))['data']

        #splits tags and genres into seperate lists
        genre = animeData['GenreCollection']
        tags = animeData['MediaTagCollection']

        #removes the 'name' portion in the list to make it identical to the genre list
        for x in range(0, len(tags)):
            tags[x] = tags[x]['name']                   

        genreTags = [genre, tags]

        return genreTags
