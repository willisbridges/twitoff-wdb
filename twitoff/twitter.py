import tweepy
from os import getenv
from .models import DB
from .models import Tweet
from .models import User
import spacy


# Get our API keys
key = getenv("TWITTER_API_KEY")
secret = getenv("TWITTER_API_KEY_SECRET")

# Authenticate with Twitter
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)

# Open a connection to the API
TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):
    # Get the user data from twitter
    try:
        twitter_user = TWITTER.get_user(screen_name=username)

        # Check to see if this user is already in the database
        # If they're alread in the DB, do nothing.
        # If they're not in the DB, insert them.
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, username=username))

        # This if statement is equivalent to the above expression
        # if User.query.get(twitter_user.id):
        #     db_user = User.query.get(twitter_user.id)
        # else:
        #     db_user = User(id=twitter_user.id, username=username)

        DB.session.add(db_user)

        # get the user's tweets from their "timeline"
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        # assign newest_tweet_id
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # add the individual tweets to the DB
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             user_id=db_user.id,
                             vect=tweet_vector)

            DB.session.add(db_tweet)

    # Final step to save the DB
    except Exception as error:
        print(f'Error when processing {username}: {error}')
        raise error
    else:
        DB.session.commit()


nlp = spacy.load('my_model/')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector