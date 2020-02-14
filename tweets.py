import tweepy
import numpy as np
import pandas as pd
import re
import argparse
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
from datetime import date

from config import *
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def clean_tweet(tweet):
    return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)', ' ', tweet).split())

def stream(data, file_name, days_to_subtract = 0, tweets_to_get = 2000, market = 'SPY'):
    i = 0
    sum = 0

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    places = api.geo_search(query="USA",granularity="country")
    place_id = places[0].id

    dt = datetime.datetime.now() - timedelta(days=days_to_subtract)
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    search_date = dt.strftime("%Y-%m-%d")
    print("Day: ", search_date)

    df = pd.DataFrame(columns = ['tweets', 'tweets_clean', "textblob", 'vader',  'sentiment', 'sentiment_label',
                                'user', 'user_statuses_count', 
                                'user_followers', 'User_location', 
                                'fav_count', 'rt_count', 'tweet_date', 'lat', 'lng', 'place', 'country'])

    for tweet in tweepy.Cursor(api.search, tweet_mode="extended", q="place:%s" % place_id, count=100, until=search_date, lang='en').items():
        print(i, end='\r')
        df.loc[i, 'tweets'] = tweet.full_text
        cleaned = clean_tweet(tweet.full_text)
        df.loc[i, 'tweets_clean'] = cleaned

        analysis = TextBlob(cleaned)

        vader = SentimentIntensityAnalyzer()
        score = vader.polarity_scores(tweet.full_text)
        avg = (analysis.sentiment.polarity + score['compound']) / 2
        df.loc[i, 'sentiment'] = avg
        sum += avg

        if avg > 0.5:
            df.loc[i, 'sentiment_label'] = 'positive'
        elif avg < -0.5:
            df.loc[i, 'sentiment_label'] = 'negative'
        else:
            df.loc[i, 'sentiment_label'] = 'neutral'

        df.loc[i, 'textblob'] = analysis.sentiment.polarity
        df.loc[i, 'vader'] = score['compound']
        df.loc[i, 'user'] = tweet.user.name
        df.loc[i, 'user_statuses_count'] = tweet.user.statuses_count
        df.loc[i, 'user_followers'] = tweet.user.followers_count
        df.loc[i, 'User_location'] = tweet.user.location
        df.loc[i, 'fav_count'] = tweet.favorite_count
        df.loc[i, 'rt_count'] = tweet.retweet_count
        df.loc[i, 'tweet_date'] = tweet.created_at
        if tweet.coordinates is not None:
            if len(tweet.coordinates) > 1:
                df.loc[i, 'lat'] = tweet.coordinates['coordinates'][0]
                df.loc[i, 'lng'] = tweet.coordinates['coordinates'][1]
        if tweet.place:
            df.loc[i, 'place'] = tweet.place.full_name
            df.loc[i, 'country'] = tweet.place.country
        i+=1
        if i == tweets_to_get:

            opening_price = get_ticker_information(market, days_to_subtract)

            overall = sum / i
            stock_label = f"{market} Open"
            summary_table = pd.DataFrame({"Date": [search_date], "Sentiment": [overall], stock_label: [opening_price]})

            # Write out current date summary
            summary_table.to_csv('{}.csv'.format("summary"))
            print(summary_table)

            # Write out tweets
            df.to_csv('{}.csv'.format(file_name))

            # Append current data to history
            summary_save_df = pd.read_csv("summary_save.csv", index_col = 0)
            new_df = summary_save_df.append(summary_table, ignore_index=True)
            new_df.to_csv('{}.csv'.format("summary_save"))

            from sqlalchemy import create_engine
            engine = create_engine('sqlite:///tweets.sqlite', echo=False)

            df.to_sql('tweets', con=engine, index=False, if_exists='append')

            break

def get_ticker_information(ticker, days_to_subtract):

    url = f'https://finance.yahoo.com/quote/{ticker}/history/'
    print(url)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    results = soup.find_all('td', class_="Ta(start)")
    today = date.today() - timedelta(days=days_to_subtract)
    date_formatted = today.strftime("%b %d, %Y")
    print(date_formatted)

    d = 1
    for result in results:
        if date_formatted == result.text.strip():
            #print(result.text.strip() + ": " + str(d))
            break
        d += 6

    results = soup.find_all('td', class_="Pstart(10px)")

    opening = ""
    r = 0    
    for result in results:
        r += 1;
        if (r == d):
            #print(result.text.strip() + ": " + str(r))
            opening = result.text.strip()
            break

    return(opening)

def main(days = 0, tweets = 2000, market = 'SPY'):
    if (days > 7):
        print("Error: maximum number of days to subtract is 7.")
        return

    stream(['*'], 'my_tweets', days, tweets, market)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Tweets')
    parser.add_argument('--subtract', '-s',
        action='store', type=int,
        help='-s=[days to subtract]')

    parser.add_argument('--tweets', '-t',
        action='store', type=int,
        help='-t=[tweets to get]')

    parser.add_argument('--market', '-m',
        action='store', type=str,
        help='-m=[market]')

    args = parser.parse_args()

    days = 0
    if args.subtract:
        days = args.subtract 

    tweets = 2000
    if args.tweets:
        tweets = args.tweets 
        print(args.tweets)

    market = 'SPY'
    if args.market:
        market = args.market
        print(args.market)

    main(days, tweets, market)
