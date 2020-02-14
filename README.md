# Trade Bot

Work in progress of a trade bot based on ideas of Bollen et al. in the paper:

https://arxiv.org/pdf/1010.3003.pdf

The general idea is that there is a lag between Twitter overall sentiment and stock market performance that can be measured and predicted through Granger Causality.

tweets.py gets daily tweets and runs sentiment analysis based on two different methods: textblob and vader. The daily tweets are stored in a csv and the accumulated tweets are stored in a sqlite database. Also, a daily summary of the of the average sentiment is written out and kept for each day.

Also, Yahoo finance is scraped and the opening price is stored for SPY, which is an indexed fund of the S&P 500. It can optionally take other stock tickers.

Example:
|     |Date       |Sentiment        |SPY
|-----|-----------|-----------|-----|
|17	|1/6/20	|0.091364888	|320.49
|18	|1/7/20	|0.110241748	|323.02
|19	|1/8/20	|0.090223494	|322.94
|20	|1/9/20	|0.109435562	|326.16
|21	|1/10/20	|0.090665494	|327.29

trade.py is where future work can be done after enough daily twitter sentiment scores can be built up. trade.py can be modified to use the Alpace API to make free trades based on the algorithm

### Running tweets.py

To run the project, use the following. This defaults to running on the current day and getting today's
2,000 tweets and SPY ticker price.

python tweets.py

OPTIONAL SWITCHES:

To run and specify the number of tweets, use -t switch

python main.py -t=<number_of_tweets>

To run and a number of days in the past (max = 7), the number of days to subtract (0-7), use -s switch

python main.py -s=<days_to_subtract>

To run and specify a stock ticker (SPY is default) use -m switch

python main.py -m=<stock_ticker>
