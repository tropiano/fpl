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
 
def get_league_infos(league_id):

    url = 'https://fantasy.premierleague.com/drf/leagues-classic-standings/'+str(league_id)+'?phase=1&le-page=1&ls-page=1'
    r = requests.get(url)
    jsonResponse = r.json()
    users = jsonResponse["new_entries"]["results"]
    league_name = jsonResponse["league"]["name"]

    return league_name, users


def get_user_history(userid):
    url = 'https://fantasy.premierleague.com/drf/entry/' + str(userid) + '/history'
    r = requests.get(url)
    jsonResponse = r.json()
    seasons = jsonResponse["season"]

    return seasons


def extract_user_infos(user):

    user_info = []
    name = user['player_first_name']
    surname = user['player_last_name']
    userid = user['id']
    entry = user['entry']
    season = get_user_history(entry)
    for s in season:
        user_info.append((entry, s['season'], s['season_name'], name, surname, s['total_points'], s['rank']))
    
    return user_info


app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fpl.db'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
app.secret_key = 'T5%&/yHDfSTs'


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
    existing_league_ids = db.session.query(Leagues.league_id).all()
    league_list = [i[0] for i in existing_league_ids]
    #print league_list
    if int(league_id) in league_list:
        return redirect(url_for('league_info', league_id=league_id))
    else:
        try:
            league_name, league_users = get_league_infos(league_id)
            league_entry = Leagues(league_name=league_name, league_id=league_id, season='18-19')
        except:
            flash('League Id not found', 'error')
            return redirect(url_for('landing_page'))
        db.session.add(league_entry)
        for u in league_users:
            team_info = Teams(team_id=u['id'], league_id=u['league'], team_name=u['entry_name'], user_id=u['entry'])
            db.session.add(team_info)
            user_info = extract_user_infos(u)
            for ui in user_info:
                ui_info = Users(user_id=ui[0], season=ui[1], season_name=ui[2], name=ui[3], surname=ui[4], points=ui[5], rank=ui[6])
                db.session.add(ui_info)
        db.session.commit()        
        return redirect(url_for('league_info', league_id=league_id))


@app.route('/<league_id>')
def league_info(league_id):

    entries = []
    
    existing_league_ids = db.session.query(Leagues.league_id).all()
    league_list = [i[0] for i in existing_league_ids]
    #print league_list
    if int(league_id) not in league_list:
        flash('No data for the requested League. Insert League Id in the form below to generate data for this League', 'error')
        return redirect(url_for('landing_page'))
        
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
    
    cur=db.session.query(Leagues.league_name).filter(Leagues.league_id == league_id).all()
    entries.append(cur)
    
    return render_template('show_entries.html', entries=entries)