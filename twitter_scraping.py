import json
import time
import pandas as pd
import requests


class TwitterScraper:
    """A class to allow users to easily interface with the twitter API with minimal knowledge.
    Users simply have to initialise the class with a valid twitter bearer token then call the
    get_users_tweets() method with its parameters to retrieve the requested tweet information.
    """

    version = "0.1"
    search_url = "https://api.twitter.com/2/tweets/search/all"
    header = ""

    def __init__(self, bearer_token: str) -> None:
        """Initalises the class with the value of the users bearer_token.
        Prints version num to inform users which version they're using.
        TODO: Verify token

        Args:
            bearer_token (str): Users token required for verification by the twitter API.
        """
        self.header = {
            "Authorization": "Bearer {}".format(bearer_token)
        }  # Add verification?

        print(f"TwitterScraper v{self.version} initialised.")

    # This is essentially the main code of the project all other functions only support this.
    # Does that mean that this should go first?
    def get_users_tweets(
        self, users: list[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Function to get all tweet ID's from a given date range for a list of users.
        This is the "main" function users should interact with when using this class.

        Args:
            users (list[str]): List of twitter users to get tweets from. A list containing a single user is valid.
            start_date (str): Start timestamp of tweets to retrieve. TODO: Say what timestamp format is used.
            end_date (str): End timestamp of tweets to retrieve. TODO: Say what timestamp format is used.

        Raises:
            TypeError: Raises if list of username is specified incorrectly.

        Returns:
            pd.DataFrame: DateFrame containing 3 columns 'User', 'TweetCreated', 'TweetId'.
        """

        # Type check on users to only accept a list of strings, including single element strings.
        if not isinstance(users, list):
            raise TypeError(
                message=f"This function only accepts lists of users. {users} is not a valid list of users."
            )

        # TODO: accept other datetime formats but convert to expected format before saving as class/instance variables.
        # TODO: Accept multiple datetime formats such as "2020-01-01" and "2020-01-01-07:00:00"
        # then convert this to the twitter expected representation "2019-10-01T17:07:04.000Z"
        self._start_date = start_date
        self._end_date = end_date

        res = []

        for user in users:

            print("-" * 30)
            print(f"User: {user} Number: {users.index(user)+1} of {len(users)}")
            print("-" * 30)
            print()
            res.extend(self._users_tweets(user))

        # Convert results from list of list to DataFrame
        # TODO: return more than just tweet ID, then let users filter and choose what they want afterwards.
        tweets_df = pd.DataFrame.from_records(
            res, columns=["User", "TweetCreated", "TweetId", "Link", "Contents"]
        )

        return tweets_df

    def _connect_to_endpoint(self, query_params: dict) -> json:
        """Function sends messages to the twitter API endpoint.
        TODO: Maybe rename function to send request or something as that's what it does.

        Args:
            query_params (dict): Dictionary that contains the query details of what tweets twitter should retrieve for us.

        Raises:
            Exception: Raises if the response from Twitter is ever not just 200 OK.
            #TODO: Raise specific error type related to requests or networking

        Returns:
            response.json() (json): Returns the full message response in JSON format.
        """

        response = requests.request(
            "GET", self.search_url, headers=self.header, params=query_params
        )

        if response.status_code != 200:
            print(response)
            raise Exception(response.status_code, response.text)
        else:
            return response.json()

    def _users_tweets(self, user: str) -> list:
        """Get all results from one user.
        Is a hidden helper function that creates the query to send to twitters API
        Also controls the frequency of requests to stay under twitters limit.

        To query a single users tweets users should use the get_users_tweets
        function instead of this but with a list containing a single user.

        Args:
            user (str): A Twitter username

        Returns:
            all_results (list): List of tweets, containing username, time, ID, and text of tweet.
        """
        num_runs = 0
        all_results = []

        result_count = 100  # initialise this as a non-zero number
        # will be filled with responses from json later
        # can get a max of 100 records at a time
        # so if the results aren't 100 we ran out of things to get
        # we can halt execution after every 100 records to stay under the twitter limit.

        # Define template query dict before loop and condition.
        query_params = {
            "query": f"(from:{user} -is:retweet) ",
            "tweet.fields": "author_id,id,created_at",
            "start_time": f"{self._start_date}",
            "end_time": f"{self._end_date}",
            "max_results": "100",
        }

        while result_count == 100:

            time.sleep(4)

            # First run has no next_token parameter
            # Otherwise add next token to params dict
            if num_runs > 0:
                query_params["next_token"] = results_json["meta"]["next_token"]

            json_response = self._connect_to_endpoint(query_params)

            results = json.dumps(json_response, indent=4, sort_keys=True)
            results_json = json.loads(results)

            # append this pagnation to all results
            # all_results.append(results_json)
            result_count = results_json["meta"]["result_count"]
            num_runs = num_runs + 1

            # Only add results if they're non zero
            if result_count > 0:
                list_of_tweet_dicts = results_json["data"]

                print(
                    f"Tweet {len(all_results)} from {list_of_tweet_dicts[0]['created_at']}"
                )

                for tweet in list_of_tweet_dicts:
                    all_results.append(
                        [
                            user, 
                            tweet["created_at"], 
                            tweet["id"], 
                            f'https://twitter.com/{user}/status/{tweet["id"]}',
                            tweet["text"].replace("\\n", "\n")
                            ]
                    )

        return all_results
