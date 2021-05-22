# Crawler test

# https://gist.github.com/alexdeloy/fdb36ad251f70855d5d6

from setup_api import consumerKey, consumerSecret, accessToken, accessTokenSecret
import tweepy
import datetime
import xlsxwriter
import sys

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

username = 'RugbyScribbler'
startDate = datetime.datetime(2019, 10, 18, 0, 0, 0)
endDate =   datetime.datetime(2019, 11, 18, 0, 0, 0)

tweets = []
tmpTweets = api.user_timeline(
                            username,
                            since_id=1185187691857678337,
                            max_id=1195811463706873857
                            )
for tweet in tmpTweets:
    if tweet.created_at < endDate and tweet.created_at > startDate:
        tweets.append(tweet)

while (tmpTweets[-1].created_at > startDate):
    print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
    tmpTweets = api.user_timeline(username, max_id = tmpTweets[-1].id)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)

workbook = xlsxwriter.Workbook(username + ".xlsx")
worksheet = workbook.add_worksheet()
row = 0
for tweet in tweets:
    worksheet.write_string(row, 0, str(tweet.id))
    worksheet.write_string(row, 1, str(tweet.created_at))
    worksheet.write(row, 2, tweet.text)
    worksheet.write_string(row, 3, str(tweet.in_reply_to_status_id))
    row += 1
    print(row)

workbook.close()
print("Excel file ready")
