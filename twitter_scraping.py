import json
import time
import pandas as pd
import requests


class TwitterScraper:
    """Twitter Scraper class to fetch tweets from Twitter API.

    Attributes:
        version (str): Version information.
        search_url (str): Twitter search API URL.
        header (Dict[str, str]): Header for the API request.
    """

    version = "0.1"
    search_url = "https://api.twitter.com/2/tweets/search/all"
    header = ""

    def __init__(self, bearer_token: str) -> None:
        """Initialize TwitterScraper.

        Args:
            bearer_token (str): Bearer token for Twitter API.
        """
        self.header = {
            "Authorization": "Bearer {}".format(bearer_token)
        }  # Add verification?

        print(f"TwitterScraper v{self.version} initialised.")

    def get_users_tweets(
        self, users: list[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Fetch tweets from a list of users within a date range.
        Date format should be in the ISO 8601 standard
        e.g. "2019-10-01T17:07:04.000Z"
        TODO: Accept other datetime formats and convert

        Args:
            users (List[str]): List of Twitter usernames.
            start_date (str): Starting date in Twitter's datetime format.
            end_date (str): Ending date in Twitter's datetime format.

        Raises:
            TypeError: If 'users' is not a list.

        Returns:
            pd.DataFrame: DataFrame with fetched tweet information.
        """

        # Type check
        if not isinstance(users, list):
            raise TypeError(
                message=f"This function only accepts lists of users. {users} is not a valid list of users."
            )

        self._start_date = start_date
        self._end_date = end_date

        res = []

        for user in users:
            print("-" * 30)
            print(f"User: {user} Number: {users.index(user)+1} of {len(users)}")
            print("-" * 30)
            print()
            res.extend(self._fetch_user_tweets(user))

        # Convert results from list of list to DataFrame
        tweets_df = pd.DataFrame.from_records(
            res, columns=["User", "TweetCreated", "TweetId", "Link", "Contents"]
        )

        return tweets_df

    def _send_request(self, query_params: dict) -> json:
        """Connect to Twitter API endpoint.

        Args:
            query_params (Dict[str, str]): Query parameters for the API request.

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

    def _construct_query(self, user: str) -> Dict[str, str]:
        """Construct query parameters.

        Args:
            user (str): Twitter username.

        Returns:
            Dict[str, str]: Dictionary of query parameters.
        """
        return {
            "query": f"(from:{user} -is:retweet)",
            "tweet.fields": "author_id,id,created_at,text",
            "start_time": self._start_date,
            "end_time": self._end_date,
            "max_results": "100",
        }

    def _fetch_user_tweets(self, user: str) -> list:
        """Internal method to fetch tweets for a single user.
        Constructs query to send to twitters API
        Also controls the frequency of requests to stay under twitters limit.

        Args:
            user (str): Twitter username to fetch tweets for.

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
        query_params = self._construct_query(user)
        while result_count == 100:
            time.sleep(4)

            # First run has no next_token parameter
            # Otherwise add next token to params dict
            if num_runs > 0:
                query_params["next_token"] = results_json["meta"]["next_token"]

            json_response = self._send_request(query_params)

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
                            tweet["text"].replace("\\n", "\n"),
                        ]
                    )

        return all_results
