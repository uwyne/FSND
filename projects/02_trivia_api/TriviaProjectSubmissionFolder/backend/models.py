import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import database_exists
import json



# Enable debug mode.
DEBUG = True

# Connect to the database

DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
DB_USER = os.getenv('DB_USER', 'uwyne')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password1')
DB_NAME = os.getenv('DB_NAME', 'trivia')

DB_PATH = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=DB_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
        create_database(app.config["SQLALCHEMY_DATABASE_URI"])
    db.create_all()

'''
Question

'''
class Question(db.Model):
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)

  def __init__(self, question, answer, category, difficulty):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }

'''
Category

'''
class Category(db.Model):
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }
