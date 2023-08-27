import json
import time
import logging
import pandas as pd
import requests
from typing import List, Dict, Union

logging.basicConfig(level=logging.INFO)


class TwitterScraper:
    """Twitter Scraper class to fetch tweets from Twitter API.
    
    Attributes:
        version (str): Version information.
        search_url (str): Twitter search API URL.
        header (Dict[str, str]): Header for the API request.
    """

    version = "0.2"
    search_url = "https://api.twitter.com/2/tweets/search/all"

    def __init__(self, bearer_token: str):
        """Initialize TwitterScraper.
        
        Args:
            bearer_token (str): Bearer token for Twitter API.
        """
        self.header = {"Authorization": f"Bearer {bearer_token}"}
        logging.info(f"TwitterScraper v{self.version} initialized.")

    def get_users_tweets(self, users: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch tweets from a list of users within a date range.
        
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
            raise TypeError(f"Invalid type {type(users)} for 'users'. Should be list.")
        
        # Remove TODOs, will implement date format conversion later
        self._start_date = start_date
        self._end_date = end_date

        results = []
        for user in users:
            logging.info(f"Fetching tweets for user: {user}")
            user_results = self._fetch_user_tweets(user)
            results.extend(user_results)

        tweets_df = pd.DataFrame.from_records(
            results, columns=["User", "TweetCreated", "TweetId", "Link", "Contents"]
        )
        return tweets_df

    def _fetch_user_tweets(self, user: str) -> List[List[Union[str, int]]]:
        """Internal method to fetch tweets for a single user.
        
        Args:
            user (str): Twitter username to fetch tweets for.
        
        Returns:
            List[List[Union[str, int]]]: List of fetched tweets for the user.
        """
        all_results = []
        query_params = self._build_query_params(user)
        
        while True:
            # Dynamic rate limiting
            response_headers = self._connect_to_endpoint(query_params).headers
            time.sleep(int(response_headers.get("x-rate-limit-reset", 4)))
            
            json_response = self._connect_to_endpoint(query_params).json()
            result_count = json_response["meta"]["result_count"]

            if result_count > 0:
                list_of_tweet_dicts = json_response["data"]
                logging.info(f"Fetched {len(list_of_tweet_dicts)} tweets.")
                all_results.extend(self._parse_tweets(list_of_tweet_dicts, user))

            if "next_token" in json_response["meta"]:
                query_params["next_token"] = json_response["meta"]["next_token"]
            else:
                break

        return all_results

    def _build_query_params(self, user: str) -> Dict[str, str]:
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

    def _connect_to_endpoint(self, query_params: Dict[str, str]) -> requests.Response:
        """Connect to Twitter API endpoint.
        
        Args:
            query_params (Dict[str, str]): Query parameters for the API request.
        
        Returns:
            requests.Response: Response from Twitter API.
        """
        response = requests.get(self.search_url, headers=self.header, params=query_params)
        response.raise_for_status()
        return response

    @staticmethod
    def _parse_tweets(tweets: List[Dict[str, Union[str, int]]], user: str) -> List[List[Union[str, int]]]:
        """Parse raw tweet data to a list of lists.
        
        Args:
            tweets (List[Dict[str, Union[str, int]]]): List of raw tweet data.
            user (str): Twitter username.
        
        Returns:
            List[List[Union[str, int]]]: Parsed tweet data.
        """
        parsed = []
        for tweet in tweets:
            parsed.append([
                user,
                tweet["created_at"],
                tweet["id"],
                f"https://twitter.com/{user}/status/{tweet['id']}",
                tweet["text"].replace("\\n", "\n")
            ])
        return parsed
import json
import time
import logging
import pandas as pd
import requests
from typing import List, Dict, Union

logging.basicConfig(level=logging.INFO)


class TwitterScraper:
    """Twitter Scraper class to fetch tweets from Twitter API.
    
    Attributes:
        version (str): Version information.
        search_url (str): Twitter search API URL.
        header (Dict[str, str]): Header for the API request.
    """

    version = "0.2"
    search_url = "https://api.twitter.com/2/tweets/search/all"

    def __init__(self, bearer_token: str):
        """Initialize TwitterScraper.
        
        Args:
            bearer_token (str): Bearer token for Twitter API.
        """
        self.header = {"Authorization": f"Bearer {bearer_token}"}
        logging.info(f"TwitterScraper v{self.version} initialized.")

    def get_users_tweets(self, users: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch tweets from a list of users within a date range.
        
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
            raise TypeError(f"Invalid type {type(users)} for 'users'. Should be list.")
        
        # Remove TODOs, will implement date format conversion later
        self._start_date = start_date
        self._end_date = end_date

        results = []
        for user in users:
            logging.info(f"Fetching tweets for user: {user}")
            user_results = self._fetch_user_tweets(user)
            results.extend(user_results)

        tweets_df = pd.DataFrame.from_records(
            results, columns=["User", "TweetCreated", "TweetId", "Link", "Contents"]
        )
        return tweets_df

    def _fetch_user_tweets(self, user: str) -> List[List[Union[str, int]]]:
        """Internal method to fetch tweets for a single user.
        
        Args:
            user (str): Twitter username to fetch tweets for.
        
        Returns:
            List[List[Union[str, int]]]: List of fetched tweets for the user.
        """
        all_results = []
        query_params = self._build_query_params(user)
        
        while True:
            # Dynamic rate limiting
            response_headers = self._connect_to_endpoint(query_params).headers
            time.sleep(int(response_headers.get("x-rate-limit-reset", 4)))
            
            json_response = self._connect_to_endpoint(query_params).json()
            result_count = json_response["meta"]["result_count"]

            if result_count > 0:
                list_of_tweet_dicts = json_response["data"]
                logging.info(f"Fetched {len(list_of_tweet_dicts)} tweets.")
                all_results.extend(self._parse_tweets(list_of_tweet_dicts, user))

            if "next_token" in json_response["meta"]:
                query_params["next_token"] = json_response["meta"]["next_token"]
            else:
                break

        return all_results

    def _build_query_params(self, user: str) -> Dict[str, str]:
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

    def _connect_to_endpoint(self, query_params: Dict[str, str]) -> requests.Response:
        """Connect to Twitter API endpoint.
        
        Args:
            query_params (Dict[str, str]): Query parameters for the API request.
        
        Returns:
            requests.Response: Response from Twitter API.
        """
        response = requests.get(self.search_url, headers=self.header, params=query_params)
        response.raise_for_status()
        return response

    @staticmethod
    def _parse_tweets(tweets: List[Dict[str, Union[str, int]]], user: str) -> List[List[Union[str, int]]]:
        """Parse raw tweet data to a list of lists.
        
        Args:
            tweets (List[Dict[str, Union[str, int]]]): List of raw tweet data.
            user (str): Twitter username.
        
        Returns:
            List[List[Union[str, int]]]: Parsed tweet data.
        """
        parsed = []
        for tweet in tweets:
            parsed.append([
                user,
                tweet["created_at"],
                tweet["id"],
                f"https://twitter.com/{user}/status/{tweet['id']}",
                tweet["text"].replace("\\n", "\n")
            ])
        return parsed
