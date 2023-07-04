from ctypes import sizeof
import AniListAPI.animeList
import AniListAPI.AniListCalls
from AniListAPI.AniListAccess import *
import neuralNetwork.compileData
from neuralNetwork.neuralNet import *
from neuralNetwork.recNeuralNet import *
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr
import numpy as np
import pandas as pd
from tqdm import tqdm
import traceback
import time


nnRec = recNeuralNet()

class recommendations():
    """description of class"""

    average = None


    def calculate_similarity(anime2, dataset1, priorites={}):

        # Pre-calculate the values of anime2genretag and anime2_popularity_avg_score_recommendations
        anime2genretag = anime2[[genretag for genretag in anime2.index if genretag not in ['animeName', 'popularity', 'user_score', 'recommendations']]]
        anime2_popularity_avg_score_recommendations = (anime2['popularity'] ** 0.25) * anime2['average_score'] * (anime2['recommendations'])

        # Pre-calculate the values of anime1genretag for each anime in dataset1
        dataset1genretag = dataset1[[genretag for genretag in dataset1.columns if genretag not in ['animeName', 'popularity', 'user_score', 'recommendations']]]

        # Calculate the cosine similarity between the binary-encoded genres and tags using vectorized operations
        genres_tags_similarity = cosine_similarity(dataset1genretag, np.array(anime2genretag).reshape( 1,-1)).flatten()

        # Weight the similarity score by the user's rating for the anime in dataset 1
        similarity_score = np.sum(genres_tags_similarity * dataset1['user_score'])

        similarity_score *= anime2_popularity_avg_score_recommendations

        return similarity_score


    def findReccomended_new(priorities = {}):
        #global aniData, genresTags

        # Import necessary libraries

        tqdm.pandas()

        aniData = {}
        genresTags = {}

        # Create a dataframe using data from the AniList API
        aniData = AniListCalls.retAnimeListDet(user="")
        
        print('waiting to get a list of all the anime...')

        allAnime = AniListCalls.getAllAnime(remNonPTW=True)


        print('waiting to get a list of genre tags')
        
        genresTags = AniListCalls.getAllGenreTags()

        print('got list of genretags')

        # Extract genres and tags from the data
        genres = genresTags[0]
        tags = genresTags[1]

        # Initialize dictionaries to store watched anime and recommendations
        watchedDict = {}
        rec_scores = {}

        # Process each entry in the aniData list
        for x in aniData:

            # Only consider entries with status 'DROPPED' or 'COMPLETED'
            if(x['status'] == 'DROPPED' or x['status'] == 'COMPLETED'):
                # Process each anime in the entries list
                for anime in x['entries']:
                    # Extract the name of the anime
                    name = anime['media']['title']['userPreferred']

                    # Initialize a dictionary to store data for this anime
                    diction = {}
                    diction['animeName'] = name

                    # Initialize genre and tag data for this anime
                    for genre in genres:
                        diction.setdefault(genre, 0)
                    for tag in tags:
                        diction.setdefault(tag, 0)

                    # Set genre and tag data for this anime based on the data from the API
                    for genre in anime['media']['genres']:
                        if(genre in diction):
                            diction[genre] = 1
                    for tag in anime['media']['tags']:
                        if(tag['name'] in diction):
                            diction[tag['name']] = tag['rank']/100

                    # Set average score and popularity data for this anime based on the data from the API
                    diction['average_score'] = anime['media']['averageScore']
                    diction['popularity'] = math.log(anime['media']['popularity'] + 1, 2)

                    # Set user score data for this anime based on the data from the API
                    diction['user_score'] = anime['media']['mediaListEntry']['score']

                    # Process recommendations for this anime from the API data
                    for recs in anime['media']['recommendations']['edges']:
                        if(recs['node']['mediaRecommendation'] != None):
                            rec_name = recs['node']['mediaRecommendation']['title']['userPreferred']
                            rating = recs['node']['rating']

                            # Update recommendations dictionary with data from this recommendation
                            if(rec_name not in rec_scores):
                                if(rating < 0 or diction['user_score'] < 0.7):
                                    rec_scores.setdefault(rec_name, 0)
                                else:
                                    rec_scores.setdefault(rec_name, valManip.logKeepNeg(rating+1) * (diction['user_score']/10 + 0.3))
                            else:
                                if(rating < 0):
                                    continue
                                else:
                                    if(diction['user_score'] >= 0.7):
                                        rec_scores[rec_name] += valManip.logKeepNeg(rating + 1) * (diction['user_score']/10 + 0.3)

                    # Add this anime's data to the watchedDict dictionary
                    watchedDict[name] = diction


                    

        # Initialize a dictionary to store data for all anime
        allDict = {}

        # Process each anime in the allAnime list
        for anime in allAnime:
            # Extract the name of the anime
            name = anime['title']['userPreferred']

            # Initialize a dictionary to store data for this anime
            diction = {}
            diction['animeName'] = name

            # Initialize genre and tag data for this anime
            for genre in genres:
                diction.setdefault(genre, 0)
            for tag in tags:
                diction.setdefault(tag, 0)

            # Set genre and tag data for this anime based on the data from the API
            for genre in anime['genres']:
                if(genre in diction):
                    diction[genre] = 1
            for tag in anime['tags']:
                if(tag['name'] in diction):
                    diction[tag['name']] = tag['rank']/100

            # Set average score and popularity data for this anime based on the data from the API
            diction['average_score'] = anime['averageScore']
            diction['popularity'] = math.log(anime['popularity'] + 1, 2)

            # Add this anime's data to the allDict dictionary
            allDict[name] = diction

        # Create a dataframe of recommendations from the recommendations dictionary
        names = pd.DataFrame(rec_scores.keys(), columns=['animeName'])
        scores = pd.DataFrame(rec_scores.values(), columns=['recommendations'])
        recs = names.join([scores])

        # Normalize recommendation scores using a square root transformation
        recs['recommendations'] = ((recs['recommendations'] - recs['recommendations'].min())/(recs['recommendations'].max() - recs['recommendations'].min())) ** 0.5 + 1

        # Create dataframes from the watchedDict and allDict dictionaries
        training_set = pd.DataFrame(watchedDict.values())
        all_set = pd.DataFrame(allDict.values())

        # Merge recommendation data into the training_set and all_set dataframes
        #print(training_set.head())
        training_set = training_set.merge(recs, how='left', on="animeName").fillna(1)
        all_set = all_set.merge(recs, how='left', on="animeName").fillna(1)

        # Normalize user scores in the training_set dataframe using a square root transformation
        training_set['user_score'] = (training_set['user_score'] - training_set['user_score'].mean())/training_set['user_score'].std()
        training_set['user_score'] = training_set['user_score'].apply(lambda x: valManip.sqrtKeepNeg(x))

        # Calculate the minimum and maximum popularity values across both dataframes
        popularity_min = min(training_set['popularity'].min(), all_set['popularity'].min())
        popularity_max = max(training_set['popularity'].max(), all_set['popularity'].max())

        # Replace average scores of 1 in the all_set dataframe with the mean average score (its a 1 if the anime is unwatched for somereason)
        all_set['average_score'][all_set['average_score'] == 1] = all_set['average_score'].mean()

        # Normalize average scores in both dataframes by dividing by 100
        training_set['average_score'] = training_set['average_score']/100
        all_set['average_score'] = all_set['average_score']/100

        # Normalize popularity values in both dataframes
        training_set['popularity'] = (training_set['popularity'] - popularity_min) / (popularity_max - popularity_min) + 1
        all_set['popularity'] = (all_set['popularity'] - popularity_min) / (popularity_max - popularity_min) + 1

        # Create copies of the training_set and all_set dataframes
        dataset1 = training_set.copy()
        new_set = all_set.copy()

        # Apply priority weights to tag data in both dataframes based on the priorities dictionary
        for priority_weight in priorities:
            for tag in priorities[priority_weight]:
                if(priority_weight > 1):
                    dataset1.loc[dataset1['user_score'] < 0, tag] = 0
                    dataset1.loc[dataset1['user_score'] >= 0, tag] *= priority_weight
                    new_set[tag] *= priority_weight
                elif(priority_weight < 0):
                    dataset1.loc[dataset1['user_score'] < 0, tag] *= priority_weight *-1
                    dataset1.loc[dataset1['user_score'] >= 0, tag] = 0
                    new_set[tag] *= priority_weight * -1

        # Calculate similarity scores for each anime in the new_set dataframe using the calculate_similarity function
        new_set['similarity_score'] = new_set.progress_apply(lambda x: recommendations.calculate_similarity(x, dataset1, priorites=priorities), axis=1)

        # Sort the new_set dataframe by similarity score in descending order
        new_set = new_set.sort_values(by="similarity_score", ascending=False)

        #print(new_set.head(n=10))
        #print(new_set['animeName'].head(n=10))

        # Return a list of recommended anime names from the new_set dataframe
        return new_set['animeName']





    def findReccomended(priority_genres = None, priority_tags = None, restrict_genres = None, restrict_tags = None):
        '''uses neural network to recommend anime. A list of anime is returned sorted from best to worst. It is not recommended to use this due to the insane amount of inputs relative to the amount of anime a person watches'''
        global nnRec



        true_start = time.time()

        progress = 0
        print(str(int(progress)) + "% done", end="\r")
        
        nn = recNeuralNet()
        userDataSets = ["MicchiMi", AniListAccess.getUserName(), "kotodama13", "snowwww", "Leonny", "shayoomshi", "g1appiah", "yuzurha"]

        if(nn.isNewModel()): #if a new model was created, train the neural net. If a new model was not created, use the previously trained network.
            for user in userDataSets:
                nn.addDataSet(user)
                
                print(str(int(progress + 15/len(userDataSets))) + "% done", end="\r")
                progress = 15
                #print(user)

            nnRec.train()

        stats = recommendations.getGenreTagValues(remove_outliers=True, progress_bar_start=progress, progress_bar_end=30)
        genreListStat = stats[0]
        tagListStat = stats[1]
        tagRankStat = stats[2]
        recListStat = stats[3]
        #animeCount = stats[4]
        detListPTW = stats[5]
        average = stats[6]

        #print("average: " + str(average))

        #weight the more newly watched animes in each genre more than the others
        genre_means = {}

        start = time.time()


        progress = 30
        print(str(int(progress)) + "% done", end="\r")

        slices = 10/len(genreListStat)
        
        #loop through each genre
        for genre_title in genreListStat:
            
            genre_vals = genreListStat[genre_title] 

            try:
                size = len(genre_vals)
            except:
                size = 1
                genre_vals = [genreListStat[genre_title]]
            
            weighted_count = 0
            total = 0

            '''create identical slices based on the amount in the genre.
               The weighting of the anime goes from 3x to the most recent anime down to 1x for the oldest
               anime in the genre. The weighting only applies to up to the most recent 30 anime completed.
               Everything older than the 30 anime will have 1x weighting.
               If there is less than 20 anime in the genre, the weighting starts from 2x.
               If there is less than 10 anime in the genre, the weighting starts from 1.5x'''
            max = 3 if size > 20 else 2 if size > 10 else 1.5
            min = 1
            size = 30 if size > 30 else size
            slice_size = (max-min)/size
            curr = max
            
            slices2 = slices/len(genre_vals)


            for score in reversed(genre_vals):
                total += valManip.powKeepNeg(score - average,2) * curr
                weighted_count += curr

                progress += slices2
                print(str(int(progress)) + "% done", end="\r")
                
                
                if(curr > 1):
                    curr -= slice_size

            weighted_average = valManip.powKeepNeg(total/weighted_count,0.5)
            

            #scale the value so it would rarely go over 2
            if(weighted_average > 0):
                weighted_average /= 5/2
            else: #scale the value so it would rarely go under -2/3
                weighted_average /= 15/2

            genre_means[genre_title] = weighted_average

        genre_time = time.time() - start

        start = time.time()
        slices = 10/len(tagListStat)
        #get the average of each tag, with the weighting being based on the tag ranks
        tag_means = {}

        #loop through each tag
        for tag_title in tagListStat:

            tag_vals = tagListStat[tag_title]
            tag_ranks = tagRankStat[tag_title]

            progress += slices
            print(str(int(progress)) + "% done", end="\r")
            

            try:
                size = len(tag_vals)
            except:
                size = 1
                tag_vals = [tagListStat[tag_title]]
                tag_ranks = [tagRankStat[tag_title]]

            tag_vals = numpy.subtract(tag_vals, average)

            weighted_average = numpy.average(tag_vals, weights=tag_ranks)

            #apply the variable log multiple to add more weight to tags that have been more prevalent
            if(size > 10):
                multi = math.log(size, 12)
            else:
                multi = (1/18) * size + (4/9)

            weighted_average *= multi

            #scale the value so it would rarely go over 1
            if(weighted_average > 0):
                weighted_average /= 5
            else: #scale the value so it would rarely go below -0.5x
                weighted_average /= 10


            tag_means[tag_title] = weighted_average

        tag_time = time.time() - start

        start = time.time()

        #prioritizes certain genres by increasing the mean by 3/2.5 (or making it 3/2.5 if the mean is less than 0)
        for genre in priority_genres:
            if(genre in genre_means and genre_means[genre] > 0):
                genre_means[genre] += 3/2.5
            else:
                genreListStat[genre] = 3/2.5

            print(genre + " is now " + str(genre_means[genre]))

        #deprioritizes certain genres by decreasing the mean by -3/7.5 (or making it -3/7.5 if the mean is more than 0)
        for genre in restrict_genres:
            if(genre in genre_means and genre_means[genre] < 0):
                genre_means[genre] -= 3/7.5
            else:
                genre_means[genre] -= 3/7.5

            print(genre + " is now " + str(genre_means[genre]))
        
        #prioritizes certain tags by increasing the mean by 0.6 (or making it 0.6 if the mean is less than 0)
        for tag in priority_tags:
            if(tag in tag_means and tag_means[tag] > 0):
                tag_means[tag] += 3/2.5
            else:
                tag_means[tag] = 3/2.5

            print(tag + " is now " + str(tag_means[tag]))

        #deprioritizes certain tags by decreasing the mean by 0.3 (or making it -0.3 if the mean is more than 0)
        for tag in restrict_tags:
            if(tag in tag_means and tag_means[tag] < 0):
                tag_means[tag] -= 0.3
            else:
                tag_means[tag] = -0.3

            print(tag + "is now " + str(tag_means[tag]))

        #print(genre_means)
        #print(tag_means)

        #iterate through all anime and apply equation
        list_rec = {}
        anime_info = np.array([])
        anime_titles = np.array([])
        slices = 45/len(detListPTW)

        for anime in detListPTW:
            
            #print(anime)

            progress += slices
            print(str(int(progress)) + "% done", end="\r")
            
            #skip anime that have been completed, are dropped, or are being currently watched
            if(anime['mediaListEntry'] is not None):

                status = anime['mediaListEntry']['status']
                
                if(status == "COMPLETED" or status == "DROPPED" or status == "CURRENT"):
                    continue

            title = anime['title']['userPreferred']
            score = anime['averageScore']
            if(score is None):
                continue


            #does not include the anime if the anime doesn't have a priority genre (if given).
            #Also skips the anime if the anime if it contains a restricted genre (even if it contains priority genre)
            has_genre = True
            has_res_genre = False
            for priority_genre in priority_genres:
                if(priority_genre not in anime['genres']):
                    has_genre = False
                    break
            
            for restrict_genre in restrict_genres:
                if(restrict_genre in anime['genres']):
                    has_res_genre = True
                    break

            if(has_res_genre):
                continue

            
            #does not include the anime if the anime doesn't have a priority tag (if given).
            #Also skips the anime if the anime if it contains a restricted tag (even if it contains priority tag)
            if(len(priority_tags) > 0):
                has_tag = False
            else:
                has_tag = True
            
            has_res_tag = False

            for restrict_tag in restrict_tags:

                for tag in anime['tags']:
                    tag_title = tag['name']
                    tag_rank = tag['rank']

                    if(tag_title == restrict_tag and tag_rank > 20):
                        has_res_tag = True
                        break
                
                if(has_res_tag):
                    break

            if(has_res_tag):
                continue

            for priority_tag in priority_tags:
                
                for tag in anime['tags']:
                    
                    tag_title = tag['name']
                    tag_rank = tag['rank']
                    
                    if(tag_title == priority_tag and tag_rank > 40):
                        has_tag = True
                        break
                
                if(has_tag):
                    break


            if(not has_tag or not has_genre):
                continue

            #get genre values
            genreVal = 1
            for genre in anime['genres']:

                try:
                    genreVal *= (1 + genre_means[genre])
                except:
                    pass
                    #print("%s genre excluded/ignored" % genre)

            #get tag value
            tagVal = 1
            for tag in anime['tags']:

                tag_title = tag['name']
                tag_rank = tag['rank']
                try:
                    tagVal *= (1 + (tag_means[tag_title] * (tag_rank/100)))
                except:
                    pass
                    #print("%s tag exclused/ignored" % tag_title)

            #get user recommendations
            recVal = 1
            if title in recListStat:
                for values in recListStat[title]:
                    #print(values)
                    recVal *= 1 + ((values[0] * (values[1] - average)/5))

            else:
                pass
                #print("%s has no user recommendations" % title)

            
            anime_info = np.append(anime_info, [genreVal, tagVal, recVal, score])
            anime_titles = np.append(anime_titles, title)

            #result_value = ((score * genreVal) ** recVal) * (tagVal) #recommendation value calculation for each anime using scores, recVals, genreVals, and tagVals
            
            #try:  
            #    result_value = int(result_value)
            #except: #print out the information about the anime that caused the result_value to fail
            #    print(result_value)
            #    print(genreVal)
            #    print(score)
            #    print(tagVal)
            #    print(recVal)
            #    print(title)
            #    exit()

        anime_info = np.reshape(anime_info, (-1,4))
        results = nnRec.predictGroup(anime_info)
        
        index = 0
        print(len(anime_info))
        print(len(results))
        for title in anime_titles:
            result_value = results[index]
            genreVal = anime_info[index][0]
            tagVal = anime_info[index][1]
            recVal = anime_info[index][2]
            score = anime_info[index][3]
            list_rec[title] = [result_value, score, genreVal, tagVal, recVal] #store all the values inside a dict

            index += 1



        calc_time = time.time() - start

        start = time.time()

        sortedRec = sorted(list_rec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest result_value to lowest
        
        slices = 5/len(detListPTW)

        #gets just the title of the anime to return
        with open("test.txt", 'w') as file:
            for x in range(0,len(sortedRec)): #gets the list titles in order
                try:
                    file.write(str(sortedRec[x]) + "\n")
                except:
                    pass
                #print(sortedRec[x])
                sortedRec[x] = str(sortedRec[x][0])
                
                progress += slices
                print(str(int(progress)) + "% done", end="\r")
            
            

        #print(sortedRec)

        sort_time = time.time() - start

        total_time = time.time() - true_start



        #print(genre_means)
        #print(tag_means)

        print("execution time to get the mean of the genres: " + str(genre_time))
        print("execution time to get the weighted average of the tags: " + str(tag_time))
        print("execution time to get evaluate all the anime: " + str(calc_time))
        print("execution time to sort the anime: " + str(sort_time))
        print("total execution time: " + str(total_time))

        return sortedRec

    def getGenreTagValues(remove_outliers = False, progress_bar_start=0, progress_bar_end=100):
        global average

        #true_start = time.time()
        progress = progress_bar_start
        print(str(int(progress)) + "% done", end="\r")


        start = time.time()

        animeListDet = animeList.getAnimeListDet(sort="FINISHED_ON") #gets the lists with genres, avg score (of others), and tags included. Not included in base list because it takes longer to call so initialization might take longer

        progress += (progress_bar_end - progress_bar_start) * 0.05
        print(str(int(progress)) + "% done", end="\r")

        detListPTW = AniListCalls.getAllAnime(True)
        end = time.time()

        print("execution time to get All Anime: " + str(end-start))

        #creates list of all genres in the list and how often they appear and how the anime are rated from the Completed List
        genreListStat = {}
        genreTotal = 0

        tagListStat = {}
        tagRankStat = {}
        tagTotal = 0

        recListStat = {}

        animeCount = 0
        totalScore = 0

        start = time.time()

        slices = (progress_bar_end - progress_bar_start) * 0.9/len(animeListDet)
        
        for detList in animeListDet: #iterates through each anime list

            if(detList['status'] == "PLANNING" or detList['status'] == "CURRENT"):
                continue

            status = detList['status']

            detList = detList['entries']
            animeCount += len(detList)

            
            slices2 = slices/len(detList)

            for detAnime in detList: #iterates through each anime and finds the genreValues and tagValues

                scoreValue = detAnime['media']['mediaListEntry']['score']

                name = detAnime['media']['title']['userPreferred']
                
                #print(status + " " + name)

                if((scoreValue) == 0):
                    animeCount -= 1
                    continue

                totalScore += scoreValue


                for genres in detAnime['media']['genres']: #gets genreValues

                    genreValue = scoreValue

                    if genres not in genreListStat:
                        genreListStat[genres] = np.array(genreValue)
                    else:
                        genreListStat[genres] = np.append(genreListStat[genres], genreValue)


                for tags in detAnime['media']['tags']: #gets tagValues

                    tagRank =  tags['rank']
                    if(tagRank < 10):
                        continue
                    tagTitle = tags['name']
                    tagValue = scoreValue

                    if tagTitle not in tagListStat:
                        tagListStat[tagTitle] = np.array(tagValue)
                        tagRankStat[tagTitle] = np.array(tagRank)
                    else:
                        tagListStat[tagTitle] = np.append(tagListStat[tagTitle], tagValue)
                        tagRankStat[tagTitle] = np.append(tagRankStat[tagTitle], tagRank)

                rating_values = np.array([])
                titles = np.array([])

                for recommendation in detAnime['media']['recommendations']['edges']:
                    recommendation = recommendation['node']

                    #print(recommendation)

                    try:
                        rating = recommendation['rating']
                        title = recommendation['mediaRecommendation']['title']['userPreferred']
                    except:
                        continue

                    if(rating <= 0):
                        continue

                    rating_values = np.append(rating_values, rating)
                    titles = np.append(titles,title)

                if(len(rating_values) == 0):
                    continue

                sum = np.sum(rating_values)
                rating_values = np.reshape(np.divide(rating_values,sum), (-1))

                for i, title in enumerate(titles):
                    if title not in recListStat:
                        #print(title)
                        recListStat[title] = np.array([[rating_values[i], scoreValue]])
                    else:
                        #print(title)
                        #print(rating_values[i])
                        #print(recListStat[title])
                        recListStat[title] = np.vstack((recListStat[title], [rating_values[i], scoreValue]))

                progress += slices2
                print(str(int(progress)) + "% done", end="\r")

        #print(recListStat[title])

        average = totalScore/animeCount

        end = time.time()
        iter_time = end-start




        start = time.time()
        if(remove_outliers):
            genreListStat = recommendations.removeOutliers(genreListStat)
            tagListStat,tagRankStat = recommendations.removeOutliers(tagListStat, weights=tagRankStat)
        end = time.time()

        progress += (progress_bar_end - progress_bar_start) * 0.05
        print(str(int(progress)) + "% done", end="\r")

        #true_end = time.time()

        print("execution time to iterate through each anime in list: " + str(iter_time))
        print("execution time to remove outliers: " + str(end-start))
        #print("total execution time: " + str(true_end - true_start))
        #print("average score: " + str(totalScore/animeCount))

        



        stats = [genreListStat, tagListStat, tagRankStat, recListStat, animeCount, detListPTW, average]

        return stats




    def removeOutliers(dict, weights=None, std_devs=1.96):
        '''removes the outliers in the data (ok well not exactly, but it removes the values outside of the 95% confidence interval (1.96 standard deviations) 
           to prevent rogue good or bad anime to skew the data too much'''

        total_deleted = 0
        total_sum = 0
        total_size = 0

        for val in dict:

            vals = dict[val]
            
            try:
                old_len = len(vals)
            except:
                old_len = 1
                vals = [vals]

            if(old_len < 5):
                continue
            
            #print("-------------------%s------------------------" % val)
            std = np.std(vals)





            if(weights is not None):
                mean = np.average(vals, weights=weights[val])
            else:
                mean = np.mean(vals)

            #print("old mean: " + str(mean))
            #print("std: " + str(std))
            #print("length: " + str(old_len))

            if(std == 0):
                continue



            arr = np.array(vals)

            if(weights is not None):
                new_arr=np.array([])
                new_weights = np.array([])
                deleted = 0

                if(std is 0.0):
                    continue

                for count, x in enumerate(arr):
                    if(x > valManip.round(mean - 1.96*std,1) and x < valManip.round(mean + 1.96*std,1)):
                        new_arr = np.append(new_arr, x)
                        try:
                            new_weights = np.append(new_weights, weights[val][count])
                        except:
                            traceback.print_exc()
                            print(count)
                    else:
                        deleted += 1

                dict[val] = new_arr
                weights[val] = new_weights


            else:
                arr = np.delete(arr, np.argwhere(arr < valManip.round(mean - 1.96*std,1)))
                arr = np.delete(arr, np.argwhere(arr > valManip.round((mean + 1.96 * std),1)))
                dict[val] = arr
                
            vals = dict[val]

            if(weights is not None):
                mean = np.average(vals, weights=weights[val])
            else:
                mean = np.mean(vals)

            total_sum += np.sum(vals)
            total_size += len(vals)

            deleted = old_len - len(vals)
            total_deleted += deleted
            
            #print("new mean: " + str(mean))
            #print("deleted: " + str(deleted))

        #print("total deleted: " + str(total_deleted))
        #new_average = total_sum/total_size
        #print("new average: " + str(new_average))

        if(weights is not None):
            return (dict, weights)
        else:
            return (dict)

    def findReccomendedLegacy(priority_genres = None, priority_tags = None, restrict_genres = None, restrict_tags = None):
        '''Original recommendation algorithm. Hand crafted based on the score, tags, and genres of an anime based on the anime you have already watched. Returns a sorted Plan to Watch list'''


        true_start = time.time()

        progress = 0
        print(str(int(progress)) + "% done", end="\r")

        stats = recommendations.getGenreTagValues(remove_outliers=True, progress_bar_start=progress, progress_bar_end=30)
        genreListStat = stats[0]
        tagListStat = stats[1]
        tagRankStat = stats[2]
        recListStat = stats[3]
        #animeCount = stats[4]
        detListPTW = stats[5]
        average = stats[6]

        #print("average: " + str(average))

        #weight the more newly watched animes in each genre more than the others
        genre_means = {}

        start = time.time()


        progress = 30
        print(str(int(progress)) + "% done", end="\r")

        slices = 10/len(genreListStat)
        
        #loop through each genre
        for genre_title in genreListStat:
            
            genre_vals = genreListStat[genre_title] 

            try:
                size = len(genre_vals)
            except:
                size = 1
                genre_vals = [genreListStat[genre_title]]
            
            weighted_count = 0
            total = 0

            '''create identical slices based on the amount in the genre.
               The weighting of the anime goes from 3x to the most recent anime down to 1x for the oldest
               anime in the genre. The weighting only applies to up to the most recent 30 anime completed.
               Everything older than the 30 anime will have 1x weighting.
               If there is less than 20 anime in the genre, the weighting starts from 2x.
               If there is less than 10 anime in the genre, the weighting starts from 1.5x'''
            max = 3 if size > 20 else 2 if size > 10 else 1.5
            min = 1
            size = 30 if size > 30 else size
            slice_size = (max-min)/size
            curr = max
            
            slices2 = slices/len(genre_vals)


            for score in reversed(genre_vals):
                total += valManip.powKeepNeg(score - average,2) * curr
                weighted_count += curr

                progress += slices2
                print(str(int(progress)) + "% done", end="\r")
                
                
                if(curr > 1):
                    curr -= slice_size

            weighted_average = valManip.powKeepNeg(total/weighted_count,0.5)
            

            #scale the value so it would rarely go over 2
            if(weighted_average > 0):
                weighted_average /= 5/2
            else: #scale the value so it would rarely go under -2/3
                weighted_average /= 15/2

            genre_means[genre_title] = weighted_average

        genre_time = time.time() - start

        start = time.time()
        slices = 10/len(tagListStat)
        #get the average of each tag, with the weighting being based on the tag ranks
        tag_means = {}

        #loop through each tag
        for tag_title in tagListStat:

            tag_vals = tagListStat[tag_title]
            tag_ranks = tagRankStat[tag_title]

            progress += slices
            print(str(int(progress)) + "% done", end="\r")
            

            try:
                size = len(tag_vals)
            except:
                size = 1
                tag_vals = [tagListStat[tag_title]]
                tag_ranks = [tagRankStat[tag_title]]

            tag_vals = numpy.subtract(tag_vals, average)

            weighted_average = numpy.average(tag_vals, weights=tag_ranks)

            #apply the variable log multiple to add more weight to tags that have been more prevalent
            if(size > 10):
                multi = math.log(size, 12)
            else:
                multi = (1/18) * size + (4/9)

            weighted_average *= multi

            #scale the value so it would rarely go over 1
            if(weighted_average > 0):
                weighted_average /= 5
            else: #scale the value so it would rarely go below -0.5x
                weighted_average /= 10


            tag_means[tag_title] = weighted_average

        tag_time = time.time() - start

        start = time.time()

        #prioritizes certain genres by increasing the mean by 3/2.5 (or making it 3/2.5 if the mean is less than 0)
        for genre in priority_genres:
            if(genre in genre_means and genre_means[genre] > 0):
                genre_means[genre] += 3/2.5
            else:
                genreListStat[genre] = 3/2.5

            print(genre + " is now " + str(genre_means[genre]))

        #deprioritizes certain genres by decreasing the mean by -3/7.5 (or making it -3/7.5 if the mean is more than 0)
        for genre in restrict_genres:
            if(genre in genre_means and genre_means[genre] < 0):
                genre_means[genre] -= 3/7.5
            else:
                genre_means[genre] -= 3/7.5

            print(genre + " is now " + str(genre_means[genre]))
        
        #prioritizes certain tags by increasing the mean by 0.6 (or making it 0.6 if the mean is less than 0)
        for tag in priority_tags:
            if(tag in tag_means and tag_means[tag] > 0):
                tag_means[tag] += 3/2.5
            else:
                tag_means[tag] = 3/2.5

            print(tag + " is now " + str(tag_means[tag]))

        #deprioritizes certain tags by decreasing the mean by 0.3 (or making it -0.3 if the mean is more than 0)
        for tag in restrict_tags:
            if(tag in tag_means and tag_means[tag] < 0):
                tag_means[tag] -= 0.3
            else:
                tag_means[tag] = -0.3

            print(tag + "is now " + str(tag_means[tag]))

        #print(genre_means)
        #print(tag_means)

        #iterate through all anime and apply equation
        list_rec = {}
        anime_info = np.array([])
        anime_titles = np.array([])
        slices = 45/len(detListPTW)

        for anime in detListPTW:
            
            #print(anime)

            progress += slices
            print(str(int(progress)) + "% done", end="\r")
            
            #skip anime that have been completed, are dropped, or are being currently watched
            if(anime['mediaListEntry'] is not None):

                status = anime['mediaListEntry']['status']
                
                if(status == "COMPLETED" or status == "DROPPED" or status == "CURRENT"):
                    continue

            title = anime['title']['userPreferred']
            score = anime['averageScore']
            if(score is None):
                continue


            #does not include the anime if the anime doesn't have a priority genre (if given).
            #Also skips the anime if the anime if it contains a restricted genre (even if it contains priority genre)
            has_genre = True
            has_res_genre = False
            for priority_genre in priority_genres:
                if(priority_genre not in anime['genres']):
                    has_genre = False
                    break
            
            for restrict_genre in restrict_genres:
                if(restrict_genre in anime['genres']):
                    has_res_genre = True
                    break

            if(has_res_genre):
                continue

            
            #does not include the anime if the anime doesn't have a priority tag (if given).
            #Also skips the anime if the anime if it contains a restricted tag (even if it contains priority tag)
            if(len(priority_tags) > 0):
                has_tag = False
            else:
                has_tag = True
            
            has_res_tag = False

            for restrict_tag in restrict_tags:

                for tag in anime['tags']:
                    tag_title = tag['name']
                    tag_rank = tag['rank']

                    if(tag_title == restrict_tag and tag_rank > 20):
                        has_res_tag = True
                        break
                
                if(has_res_tag):
                    break

            if(has_res_tag):
                continue

            for priority_tag in priority_tags:
                
                for tag in anime['tags']:
                    
                    tag_title = tag['name']
                    tag_rank = tag['rank']
                    
                    if(tag_title == priority_tag and tag_rank > 40):
                        has_tag = True
                        break
                
                if(has_tag):
                    break


            if(not has_tag or not has_genre):
                continue

            #get genre values
            genreVal = 1
            for genre in anime['genres']:

                try:
                    genreVal *= (1 + genre_means[genre])
                except:
                    pass
                    #print("%s genre excluded/ignored" % genre)

            #get tag value
            tagVal = 1
            for tag in anime['tags']:

                tag_title = tag['name']
                tag_rank = tag['rank']
                try:
                    tagVal *= (1 + (tag_means[tag_title] * (tag_rank/100)))
                except:
                    pass
                    #print("%s tag exclused/ignored" % tag_title)

            #get user recommendations
            recVal = 1
            if title in recListStat:
                for values in recListStat[title]:
                    #print(values)
                    recVal *= 1 + ((values[0] * (values[1] - average)/5))

            else:
                pass
                #print("%s has no user recommendations" % title)

            result_value = ((score * genreVal) ** recVal) * (tagVal) #recommendation value calculation for each anime using scores, recVals, genreVals, and tagVals
            
            try:  
                result_value = int(result_value)
            except: #print out the information about the anime that caused the result_value to fail
                print(result_value)
                print(genreVal)
                print(score)
                print(tagVal)
                print(recVal)
                print(title)
                exit()

            list_rec[title] = [result_value, score, genreVal, tagVal, recVal] #store all the values inside a dict

        calc_time = time.time() - start

        start = time.time()

        sortedRec = sorted(list_rec.items(), key = operator.itemgetter(1), reverse = True) #sorts the list from highest result_value to lowest
        
        slices = 5/len(detListPTW)

        #gets just the title of the anime to return
        with open("test.txt", 'w') as file:
            for x in range(0,len(sortedRec)): #gets the list titles in order
                try:
                    file.write(str(sortedRec[x]) + "\n")
                except:
                    pass
                #print(sortedRec[x])
                sortedRec[x] = str(sortedRec[x][0])
                
                progress += slices
                print(str(int(progress)) + "% done", end="\r")
            
            

        #print(sortedRec)

        sort_time = time.time() - start

        total_time = time.time() - true_start



        #print(genre_means)
        #print(tag_means)

        print("execution time to get the mean of the genres: " + str(genre_time))
        print("execution time to get the weighted average of the tags: " + str(tag_time))
        print("execution time to get evaluate all the anime: " + str(calc_time))
        print("execution time to sort the anime: " + str(sort_time))
        print("total execution time: " + str(total_time))

        return sortedRec

    def process_input(input):

        between_quote=""
        values = []
        Start = False
        for char in input:

            if(char == '"'):
                Start = not Start
                values.append(between_quote)
                between_quote = ""
            elif(Start):
                between_quote += char
            else:
                if(char is not " "):
                    between_quote += char
                else:
                    values.append(between_quote)
                    between_quote = ""

        values.append(between_quote)

        values = list(filter(None, values))



        next = ""
        legacy = False
        
        genres = []
        res_genres = []
        tags = []
        res_tags = []

        genretags = AniListCalls.getAllGenreTags()
        genre_list = genretags[0]
        tag_list = genretags[1]

        if(values[0] == "r"):
            for x in values:
                if(x == "-list"):
                    genre_list = genretags[0]
                    tag_list = genretags[1]

                    print("-----GENRES-------")
                    for genre in genre_list:
                        print(genre)
                    print("------TAGS---------")
                    for tag in tag_list:
                        print(tag)

                    return
                
                elif(x == "-glist"):
                    print("-----GENRES-------")
                    for genre in genre_list:
                        print(genre)

                    return
                
                elif(x == "-tlist"):
                    print("------TAGS---------")
                    for tag in tag_list:
                        print(tag)

                    return

                elif(x == "-g=" or x == "-genre="):
                    next = "genre"

                elif(x == "-t=" or x == "-tag="):
                    next = "tag"
                
                elif(x == "-rg=" or x == "-restrictgenre="):
                    next = "res_genre"
                
                elif(x == "-rt=" or x == "-restricttag="):
                    next = "res_tag"
                elif(x == "-l" or x== "-legacy"):
                    legacy = True

                elif(next == "genre"):
                    genres += (x.split(","))
                    next = ""
                elif(next == "res_genre"):
                    res_genres += (x.split(","))
                    next = ""
                elif(next == "tag"):
                    tags += x.split(",")
                    next = ""
                elif(next == "res_tag"):
                    res_tags += (x.split(","))
                    next = ""
                elif(next == "exp"):
                    next = ""
        else:
            return


        for genre in genres:
            if(not genre in genre_list):
                genres.remove(genre)
                print(genre + " IS NOT A VALID GENRE")

        for tag in tags:
            if(not tag in tag_list):
                tags.remove(tag)
                print(tag + " IS NOT A VALID TAG")

        if(legacy):
            recommendation_list = recommendations.findReccomendedLegacy(priority_genres=genres, priority_tags=tags, restrict_genres=res_genres, restrict_tags=res_tags)
        else:

            priorities = {'100' : [], '-100' : []}
            
            priorities[100] = genres
            priorities[100] += tags
            
            priorities[-100] = res_genres
            priorities[-100] += res_tags

            recommendation_list = recommendations.findReccomended_new(priorities=priorities)

        return recommendation_list