import os
from sqlalchemy import Column, String, Integer, create_engine, Date, Float
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date

database_name = "casting_agency"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()


def db_init(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_reboot():
    db.drop_all()
    db.create_all()
    db_init_rows()


class Actor(db.Model):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)

    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        insert(self)

    def update(self):
        update(self)

    def delete(self):
        delete(self)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age
        }


Movie_Launch = db.Table('movie_launch', db.Model.metadata,
                        db.Column('Movie_id', db.Integer, db.ForeignKey('movies.id')),
                        db.Column('Actor_id', db.Integer, db.ForeignKey('actors.id')),
                        db.Column('movie_budget', db.Float))


class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)
    actors = db.relationship('Actor', secondary=Movie_Launch, backref=db.backref('movie_launch', lazy='joined'))

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        insert(self)

    def update(self):
        update(self)

    def delete(self):
        delete(self)

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }

'''CRUD OPERATIONS'''

def insert(self):
    db.session.add(self)
    db.session.commit()


def update(self):
    db.session.commit()


def delete(self):
    db.session.delete(self)
    db.session.commit()


''' Mock Data'''


def db_init_rows():
    new_actor = (Actor(
        name='Anant',
        gender='Male',
        age=29
    ))

    new_movie = (Movie(
        title='Steps to code',
        release_date=date.today()
    ))

    movie_launch = Movie_Launch.insert().values(
        Movie_id=new_movie.id,
        Actor_id=new_actor.id,
        movie_budget=100000
    )

    new_actor.insert()
    new_movie.insert()
    db.session.execute(movie_launch)
    db.session.commit()
