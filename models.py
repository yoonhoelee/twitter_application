from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask, render_template, request
from flask_migrate import Migrate
import tweepy
from embedding_as_service_client import EmbeddingClient
import os, pickle
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv
load_dotenv()


en = EmbeddingClient(host=os.environ.get('host'), port=8989)

db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    full_name = db.Column(db.String, nullable=False)
    followers = db.Column(db.BigInteger, nullable=False)
    location = db.Column(db.String, nullable=False)
    tweets = relationship('Tweet', backref='user', lazy=True)

    def __repr__(self):
        return "< User {} {} >".format(self.id, self.username)


class Tweet(db.Model):
    __tablename__ = 'Tweet'
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String)
    embedding = db.Column(db.PickleType)
    user_id = db.Column(db.BigInteger, db.ForeignKey("User.id"))


    def __repr__(self):
        return '<Tweet {} {}>'.format(self.id, self.text)

