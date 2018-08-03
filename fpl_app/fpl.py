# all the imports
#import update_db as upd
#import fill_db as fill
#import matplotlib.pyplot as plt
#import StringIO
#import model
#import numpy as np
#import datetime
#import stripe
#abort, session, ,
from flask import Flask, g, render_template, send_file, jsonify, session, abort, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
#from wtforms import Form, BooleanField, StringField, FloatField, DateField, IntegerField, validators
 


app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fpl.db'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)



#create the models for Sqlalchemy 
class Leagues(db.Model):

    __table__ = db.Model.metadata.tables['leagues']        
    
    #teams = db.relationship('Teams', backref='league', lazy='dynamic')


class Teams(db.Model):
    
    __table__ = db.Model.metadata.tables['teams']

    #results = db.relationship('Results', backref='teams', lazy='dynamic')


class Users(db.Model):

    __table__ = db.Model.metadata.tables['users']        
        

class Stats(db.Model):

    __table__ = db.Model.metadata.tables['stats']    


class Players(db.Model):

    __table__ = db.Model.metadata.tables['players']    



db.create_all()


# views
@app.route('/')
def landing_page():
    
    return render_template('index.html')


@app.route('/', methods=['POST'])
def landing_page_post():
    
    entries = []
    
    league_id = request.form['leagueid']
    # Take the league id and call the FPL API
    # Verify the league id doesn't exist yet
    # Create the league in the DB with a call to the API
    # Populate also users with the API call
     
    #processed_text = text.upper()
    #return processed_text

    return render_template('homepage.html', entries=entries)


@app.route('/<league_id>')
def league_info(league_id):

    entries = []
    
    cur=db.session.query(Users.name, Users.surname, Teams.team_name).join(Teams,Teams.user_id==Users.user_id).filter(
          Teams.league_id == league_id).group_by(Teams.team_name).all()
    entries.append(cur)
    
    cur=db.session.query(Users.name, Users.surname, Users.points, Users.season_name).join(Teams,Teams.user_id==Users.user_id).filter(
          Teams.league_id == league_id).all()
    res_sort = sorted(cur, key = lambda x: x[2], reverse = True)   
    entries.append(res_sort)

    cur=db.session.query(Users.name, Users.surname, Users.rank, Users.season_name).join(Teams,Teams.user_id==Users.user_id).filter(
          Teams.league_id == league_id).all()    
    res_sort = sorted(cur, key = lambda x: x[2], reverse = False)  
    entries.append(res_sort)
    
    cur=db.session.query(Leagues.league_name).all()
    entries.append(cur)
    
    return render_template('show_entries.html', entries=entries)