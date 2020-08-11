import os
from sqlalchemy import Column, String, Integer, create_engine, Date, Float
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date

database_name = "casting_agency"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()


def db_init(app):
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
    actor1 = (Actor(
        name='Anant',
        gender='Male',
        age=29))

    actor2 = (Actor(
        name='SRK',
        gender='Male',
        age=55
    ))
    actor3 = (Actor(
        name='TomCrusie',
        gender='Male',
        age=58
    ))

    movie1 = (Movie(
        title='Steps to code',
        release_date=date.today()
    ))
    movie2 = (Movie(
        title='My name is Khan',
        release_date=date.today()
    ))
    movie3 = (Movie(
        title='MI-3',
        release_date=date.today()
    ))

    movie_launch1 = Movie_Launch.insert().values(
        Movie_id=movie1.id,
        Actor_id=actor1.id,
        movie_budget=100000
    )

    movie_launch2 = Movie_Launch.insert().values(
        Movie_id=movie2.id,
        Actor_id=actor2.id,
        movie_budget=10000000
    )

    movie_launch3 = Movie_Launch.insert().values(
        Movie_id=movie3.id,
        Actor_id=actor3.id,
        movie_budget=10000000000
    )

    actor1.insert()
    actor2.insert()
    actor3.insert()
    movie1.insert()
    movie2.insert()
    movie3.insert()
    db.session.execute(movie_launch1)
    db.session.execute(movie_launch2)
    db.session.execute(movie_launch3)
    db.session.commit()
