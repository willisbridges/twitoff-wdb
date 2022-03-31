from .models import User
import numpy as np
from sklearn.linear_model import LogisticRegression
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):

    #query for two users from DB
    user0 = User.Query.filter(User.username == user0_username).one()
    user1 = User.Query.filter(User.username == user1_username).one()

    #get word embeddings from users tweets
    user0_vect = np.array([tweet.vector for tweet in user0.tweets])
    user1_vect = np.array([tweet.vector for tweet in user1.tweets])

    #combine their vectorizations into big X matrix
    X = np.vstack([user0_vect, user1_vect])

    #create 0s and 1s to generate a target vector
    #0s first, 1s second
    y= np.concatenate([np.zeros(len(user0)), np.ones(len(user1.tweets))])

    #train log reg
    log_reg = LogisticRegression()
    log_reg.fit(X, y)

    #get word embeedding
    #ensure 2D
    hypo_tweet_vect = np.array([vectorize_tweet(hypo_tweet_text)])

    #generate prediction
    prediction = log_reg.predict([hypo_tweet_vect])

    #return just the int value from inside prediction array
    return prediction[0]