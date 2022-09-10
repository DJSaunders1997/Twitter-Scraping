
import json
import time
import pandas as pd
import requests

class twitter_scraper:
    version = "0.1"
    search_url = "https://api.twitter.com/2/tweets/search/all"
    header = ""

    def __init__(self, bearer_token:str) -> None:
        # TODO: Remember that self.header is a replacement for the create_headers function
        self.header = {"Authorization": "Bearer {}".format(bearer_token)} # Add verification?

        print(f"twitter_scraper v{self.version} initialised.")


    def connect_to_endpoint(self, query_params:dict) -> json:
        # query params is a dict that tells twitter what to look for
        # this could be renamed to send request or something as I think thats what it does

        response = requests.request("GET", self.search_url, headers=self.header, params=query_params)

        print(response.status_code)
        if response.status_code != 200:
            print(response.status_code)
            raise Exception(response.status_code, response.text)
        else:
            return response.json()

    
    # Get all results from one user
    # TODO: Documentation
    # Is a hidden helper function that creates the query to send to twitters api
    # Also controls the frequency of requests to stay under twitters limit.
    #  
    # To query a single users tweets users should use the get_list_users_tweets 
    # function instead of this but with a list containing a single user 
    def _users_tweets(self, user:str, start_time:str, end_time:str) -> list:
        '''
        users - a list of twitter user
        start_time - start date + time we want #TODO: Implement
        end_time - end date + time we want   #TODO: Implement
        '''
        num_runs = 0
        all_results = []

        result_count = 100  # initilise this as a non-zero number
                            # will be filled with respnses from json later 
                            # can get a max of 100 records at a time
                            # so if the results arnt 100 we ran out of things to get
                            # we can halt execution after every 100 records to stay under the twitter limit. 

        while result_count == 100:

            time.sleep(4)

            if num_runs ==0:
                # No next_token parameter
                query_params = {
                        'query': f'(from:{user} -is:retweet) ',
                        'tweet.fields': 'author_id,id,created_at',
                        "start_time":"2019-10-01T07:20:50.52Z",
                        "end_time":"2019-11-01T07:20:50.52Z",
                        "max_results": "100"
                }
            else:
                # with next_token
                query_params = {
                        'query': f'(from:{user} -is:retweet) ',
                        'tweet.fields': 'author_id,id,created_at',
                        "start_time":f"{start_time}",
                        "end_time":f"{end_time}",
                        "max_results": "100",
                        "next_token": results_json['meta']['next_token']
                }

            json_response = self.connect_to_endpoint(query_params)

            results = json.dumps(json_response, indent=4, sort_keys=True)
            results_json = json.loads(results)

            # append this pagnation to all results
            #all_results.append(results_json)
            result_count = results_json['meta']['result_count']
            num_runs = num_runs + 1

            # Only add results if theyre non zero
            if result_count > 0:
                list_of_tweet_dicts = results_json['data']

                print(f"Tweet {len(all_results)} from {list_of_tweet_dicts[0]['created_at']}")

                for tweet in list_of_tweet_dicts:
                    all_results.append([user, tweet['created_at'], tweet['id']])

        return all_results


    # THIS IS ESSENTIALLY THE MAIN CODE OF THE PROJECT
    # ALL OTHER FUNCTIONS ONLY SUPPORT THIS 
    # DOES THAT MEAN THAT THIS SHOULD GO FIRST?
    # TODO: Think whether a list of users should be specified here, 
    #       or whether it should be specified as a class variable earlier
    # TODO: Accept multiple datetime formats such as "2020-01-01" and "2020-01-01-07:00:00"
    #       then convert this to the twitter expected representation "2019-10-01T17:07:04.000Z"
    def get_list_users_tweets(self, users:list[str], start_date:str, end_date:str) -> pd.DataFrame:
        '''
        Function to get all tweet ID's from a given date range for a list of users.

        users - a list of twitter users. A list containing a single user is acceptable.
        start_date - start date + time we want
        end_date - end date + time we want
        '''

        #Type check on users to only accept a list of strings, including single element strings.
        if not isinstance(users, list):
            raise TypeError(message=f"This function only accepts lists of users. {users} is not a valid list of users.")

        res = []

        for user in users:
            
            print('-'*30)
            print(f"User: {user} Number: {users.index(user)+1} of {len(users)}")
            print('-'*30)
            print()
            # Append results of function to results
            # Extend will insure everything is in the same list
            # Append would create a list of lists
            res.extend( self._users_tweets(user, start_date, end_date ) )

        #Convert results from list of list to DataFrame
        # TODO: return more than just tweet ID, then let users filter and choose what they want afterwards.
        tweets_df = pd.DataFrame.from_records(res, columns=['User', 'TweetCreated', 'TweetId'])

        return tweets_df
