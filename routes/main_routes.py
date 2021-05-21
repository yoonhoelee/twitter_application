from flask import Flask, render_template, request, Blueprint
from twit_app.models import User, Tweet, en, db
from sklearn.linear_model import LogisticRegression
import os, pickle
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import tweepy


apikey= os.environ.get('apikey')
apipw = os.environ.get('apipw')
accesstoken = os.environ.get('accesstoken')
accesspw = os.environ.get('accesspw')

auth=tweepy.OAuthHandler(apikey, apipw)
auth.set_access_token(accesstoken, accesspw)
api = tweepy.API(auth)

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def welcome():
   return render_template("index.html")

@main_routes.route('/users/')
def users():
    data = User.query.all()
    return render_template("users.html", data = data)


@main_routes.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            db.create_all()
            x = request.form.get("username")
            newuser = api.get_user(screen_name=x)
            user = User(id = newuser.id, username = newuser.screen_name, full_name = newuser.name, followers = newuser.followers_count, location = newuser.location)
            db.session.add(user)
            db.session.commit()
            newtweet = api.user_timeline(screen_name=x)[0]
            tweet = Tweet(text = newtweet.text, embedding = en.encode(texts=[newtweet.text]), user_id=user.id)  
            db.session.add(tweet)          
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Failed to add user")
            print(e)

    users = User.query.all()
    return render_template("add.html", users = users)

    
@main_routes.route('/delete')
def delete():
    db.drop_all()
    db.create_all()
    return 'DB deleted'

@main_routes.route('/update/', methods=["GET", "POST"])
def update():
	if request.method == "POST":
		print(dict(request.form))
		result = request.form
		db.session.query(User).filter(User.username == result['username']).update({'username': result['change_name']})
		db.session.commit()
	
	return render_template('update.html')


@main_routes.route('/compare', methods=["GET", "POST"])
def compare():
    users=User.query.all()
    prediction=""
    input_tweet=""

    if request.method == "POST":
        tweet_user1=request.form["user_1"]
        tweet_user2=request.form["user_2"]
        
        X=[]
        y=[]
        
        user_1=User.query.filter_by(username=tweet_user1).one()
        user_2=User.query.filter_by(username=tweet_user2).one()
        
        for tweet1 in user_1.tweets:
            X.append(tweet1.embedding.flatten())
            y.append(user_1.username)
        
        for tweet2 in user_2.tweets:
            X.append(tweet2.embedding.flatten())
            y.append(user_2.username)
        
        model= LogisticRegression()
        model.fit(X,y)

        input_tweet=request.form["input_tweet"]
        prediction=model.predict(en.encode(texts=[input_tweet]))

        print(f"Prediction Reuslts [prediction]")
        
    return render_template('compare.html', users=users, prediction=prediction, input_tweet=input_tweet)
