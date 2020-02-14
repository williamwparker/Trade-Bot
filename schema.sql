CREATE TABLE tweets (
	id INT IDENTITY(1,1) PRIMARY KEY,
	tweets	TEXT,
	tweets_clean	TEXT,
	textblob	TEXT,
	vader REAL,
	sentiment	REAL,
	sentiment_label	TEXT,
	[user] TEXT,
	user_statuses_count	INT,
	user_followers INT,
	user_location	TEXT,
	fav_count	INT,
	rt_count	INT,
	tweet_date	TEXT,
	lat	REAL,
	lng	REAL,
	place	TEXT,
	country	TEXT
);
