# 🚀 Twitter-Scraping
Just a test to see about scraping info from twitter. Will update description as this use case develops.

## 🤔 How To Use

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DJSaunders1997/Twitter-Scraping/HEAD?labpath=.%2Fbinder_notebook.ipynb)

👆 Easily run the code through binder. Simply replace <enter-your-key-here> with your twitter api key!
 
## 💡 Full Archive Search

This script allows you to search for tweets within a specified date range for a list of users. The script imports the necessary libraries, sets up the bearer token, and provides a function to perform the search.

## 📚 Dependencies

To run this script, you will need the following dependencies installed in your environment:
- pandas
- requests
- jupyter (optional, if you want to use Jupyter Notebook)

To install the dependencies, you can use the provided `requirements.yml` file to create a conda environment or install the packages using `pip`.

## 🚀 Usage

1. Obtain a Twitter bearer token from the Twitter Developer Dashboard and store it as an environment variable.
2. Import the `twitter_scraper` class from the `twitter_scraping.py` file.
3. Initialize the class with your bearer token.
4. Call the `get_users_tweets` method with a list of Twitter usernames and the desired date range.
5. The method will return a pandas DataFrame with columns for the username, tweet creation time, and tweet ID.

## 📖 Example

Here's an example of how to use the script to search for tweets from a list of users:

```
from twitter_scraping import twitter_scraper

bearer_token = os.environ["twitter_bearer_token"]
ts = twitter_scraper(bearer_token)
users = ["nigel_farage", "CNNChile"]
start_date = "2019-10-01T00:00:00.00Z"
end_date = "2019-11-01T00:00:00.00Z"
tweets_df = ts.get_users_tweets(users, start_date, end_date)
```

## 📂 Output

The DataFrame can be exported to a CSV file for further analysis:

```
tweets_df.to_csv("output.csv")
```
