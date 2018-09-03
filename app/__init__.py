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
import requests
import os
#from wtforms import Form, BooleanField, StringField, FloatField, DateField, IntegerField, validators
 
def get_league_infos(league_id):

    url = 'https://fantasy.premierleague.com/drf/leagues-classic-standings/'+str(league_id)+'?phase=1&le-page=1&ls-page=1'
    r = requests.get(url)
    jsonResponse = r.json()
    users = jsonResponse["standings"]["results"]
    league_name = jsonResponse["league"]["name"]
    if len(users) <= 40:
        return league_name, users


def get_user_history(userid):
    url = 'https://fantasy.premierleague.com/drf/entry/' + str(userid) + '/history'
    r = requests.get(url)
    jsonResponse = r.json()
    seasons = jsonResponse["season"]

    return seasons


def extract_user_infos(user):

    user_info = []
    #print user
    name = user['player_name'].split(" ")[0]
    surname = user['player_name'].split(" ")[1]
    userid = user['id']
    entry = user['entry']
    season = get_user_history(entry)
    for s in season:
        user_info.append((entry, s['season'], s['season_name'], name, surname, s['total_points'], s['rank']))
        
    url = 'https://fantasy.premierleague.com/drf/entry/' + str(entry)
    r = requests.get(url)
    jsonResponse = r.json()
    data = jsonResponse["entry"]
    user_info.append((entry, 13, '2018/19', name, surname, data['summary_overall_points'], data['summary_overall_rank']))
    
    return user_info


app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)
#uncomment to test locally
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/fpl'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
#db.Model.metadata.reflect(db.engine)
app.secret_key = 'T5%&/yHDfSTs'


#create the models for Sqlalchemy 
class Leagues(db.Model):
    
    __tablename__ = "leagues"
    
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(120), nullable=False)
    league_id = db.Column(db.Integer, nullable=False)
    league_name = db.Column(db.String(120), nullable=False)
    # db.UniqueConstraint('league_id', 'league_name', name='uix_1')
    # teams = db.relationship('Teams', backref='league', lazy='dynamic')


class Teams(db.Model):
    
    __tablename__ = "teams"
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    league_id = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    #results = db.relationship('Results', backref='teams', lazy='dynamic')


class Users(db.Model):

    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    season_name = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    
        

class Stats(db.Model):

    __tablename__ = "stats"
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    team_value = db.Column(db.Integer, nullable=False)
    bank_money = db.Column(db.Integer, nullable=False)
    gameweek = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    points_bench = db.Column(db.Integer, nullable=False)
    best_player = db.Column(db.String(120), nullable=False)
    worst_player = db.Column(db.String(120), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    rank_gw = db.Column(db.Integer, nullable=False)
    best_player_points = db.Column(db.Integer, nullable=False)
    worst_player_points = db.Column(db.Integer, nullable=False)
        


class Players(db.Model):

    __tablename__ = "players"
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    player_name = db.Column(db.String(120), nullable=False)
    player_points = db.Column(db.Integer, nullable=False)
    gameweek = db.Column(db.Integer, nullable=False)


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
    # print(league_list)
    if int(league_id) in league_list:
        return redirect(url_for('league_info', league_id=league_id))
    else:
        try:
            league_name, league_users = get_league_infos(league_id)
            # print(league_users)
            
            league_entry = Leagues(league_name=league_name, league_id=league_id, season='18-19')
        except Exception as e:
            print(e)
            flash('League Id not found or League has more than 40 users', 'error')
            return redirect(url_for('landing_page'))
        db.session.add(league_entry)
        for u in league_users:
            team_info = Teams(team_id=u['id'], league_id=u['league'], team_name=u['entry_name'], user_id=u['entry'])
            #print team_info.team_name
            db.session.add(team_info)
            user_info = extract_user_infos(u)
            for ui in user_info:
                exists = db.session.query(Users.user_id).filter(Users.user_id == ui[0]).filter(Users.season == ui[1]).first() is not None
                if not exists:
                    ui_info = Users(user_id=ui[0], season=ui[1], season_name=ui[2], name=ui[3], surname=ui[4], points=ui[5], rank=ui[6])
                    db.session.add(ui_info)
        db.session.commit()        
        return redirect(url_for('league_info', league_id=league_id))


@app.route('/league/<league_id>')
def league_info(league_id):

    entries = []
    
    existing_league_ids = db.session.query(Leagues.league_id).all()
    league_list = [i[0] for i in existing_league_ids]
    #print league_list
    if int(league_id) not in league_list:
        flash('No data for the requested League. Insert League Id in the form below to generate data for this League', 'error')
        return redirect(url_for('landing_page'))
        
     
    cur=db.session.query(Users.name, Users.surname, Teams.team_name, Stats.gameweek, Stats.points.label('gw_points'), 
    Users.points, Stats.team_value, Stats.points_bench, Users.user_id).distinct(Users.name).join(
    Teams,Teams.user_id==Users.user_id).join(Stats,Stats.team_id==Teams.team_id).filter(Users.season == 13).order_by(
    Users.name, Stats.gameweek.desc()).all()

    cur_order = sorted(cur, key= lambda x: x[5],reverse=True)
    entries.append(cur_order)
    
    #print cur
    
    cur=db.session.query(Users.name, Users.surname, Users.points, Users.season_name).join(Teams,Teams.user_id == Users.user_id).filter(
          Teams.league_id == league_id).filter(Users.season != 13).all()
    res_sort = sorted(cur, key = lambda x: x[2], reverse = True)   
    entries.append(res_sort)

    cur=db.session.query(Users.name, Users.surname, Users.rank, Users.season_name).join(Teams,Teams.user_id==Users.user_id).filter(
          Teams.league_id == league_id).filter(Users.season != 13).all()    
    res_sort = sorted(cur, key = lambda x: x[2], reverse = False)  
    entries.append(res_sort)
    
    cur=db.session.query(Leagues.league_name).filter(Leagues.league_id == league_id).all()
    entries.append(cur)
    
    cur=db.session.query(Users.name, Users.surname, Stats.rank_gw, Stats.rank, Teams.team_id, Stats.points).distinct(
        Teams.team_id).join(Teams, Teams.user_id==Users.user_id).join(
        Stats, Teams.team_id==Stats.team_id).filter(Teams.league_id == league_id).filter(
        Stats.rank_gw != 0).order_by(Teams.team_id, Stats.gameweek.desc()).all()
    print(cur)
    res_sort = sorted(cur, key = lambda x: x[2], reverse = False)
    entries.append(res_sort)
    res_sort = sorted(cur, key = lambda x: x[3], reverse = False)
    entries.append(res_sort)
    
    return render_template('show_league.html', entries=entries)

  
@app.route('/user/<user_id>')
def user_info(user_id):

    entries = []
    
    cur = db.session.query(Users.name, Users.surname, Users.season_name, Users.points, Users.rank).filter(
          Users.user_id == user_id).filter(Users.season != 13).order_by(Users.season).all()
    entries.append(cur)

    cur=db.session.query(Users.name, Users.surname, Teams.team_name, Stats.bank_money, Users.points, 
    Stats.gameweek, (Stats.team_value/10.).label('team_value'), Users.user_id).distinct(Users.name).join(
    Teams,Teams.user_id==Users.user_id).join(Stats,Stats.team_id==Teams.team_id).filter(Users.season == 13).order_by(
    Users.name, Stats.gameweek.desc()).all() 
    entries.append(cur)

    if not entries[0]:
        flash('No data for the requested User', 'error')
        return redirect(url_for('landing_page'))
        
    seasons = sorted(entries[0], key=lambda x: x.points)
    best_season = seasons[-1]
    worst_season = seasons[0]
    #print best_season
    
    return render_template('show_user.html', entries=entries, best=best_season, worst=worst_season)