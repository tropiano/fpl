#import sqlite3
#import pandas as pd
#import model
import requests
import psycopg2
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# Connecting to the database file
db = create_engine(os.environ['DATABASE_URL'])
Base = declarative_base()
Session = sessionmaker(db)  
session = Session()


class Stats(Base):

    __tablename__ = "stats"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, nullable=False)
    season = Column(Integer, nullable=False)
    team_value = Column(Integer, nullable=False)
    bank_money = Column(Integer, nullable=False)
    gameweek = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    points_bench = Column(Integer, nullable=False)
    best_player = Column(String(120), nullable=False)
    worst_player = Column(String(120), nullable=False)
    rank = Column(Integer, nullable=False)
    rank_gw = Column(Integer, nullable=False)
    best_player_points = Column(Integer, nullable=False)
    worst_player_points = Column(Integer, nullable=False)


class Users(Base):

    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    season = Column(Integer, nullable=False)
    season_name = Column(String(120), nullable=False)
    name = Column(String(120), nullable=False)
    surname = Column(String(120), nullable=False)
    points = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)
    

class Teams(Base):
    
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, nullable=False)
    league_id = Column(Integer, nullable=False)
    team_name = Column(String(120), nullable=False)
    user_id = Column(Integer, nullable=False)


def get_user_info(userid, i):
    
    url = 'https://fantasy.premierleague.com/drf/entry/' + str(userid[0]) + '/event/' + str(i) + '/picks'
    r = requests.get(url)
    jsonResponse = r.json()
    data = jsonResponse["entry_history"]
    team_stats = Stats(team_id=userid[2], season=13, team_value=data['value'], bank_money=data['bank'], gameweek=data['event'], points=data['points']-data['event_transfers_cost'], points_bench=data['points_on_bench'], best_player='', worst_player='', rank=data['overall_rank'], rank_gw=data['rank'], best_player_points=0, worst_player_points=0)    
    
    return team_stats


def get_league_infos(league_id):

    url = 'https://fantasy.premierleague.com/drf/leagues-classic-standings/'+str(league_id)+'?phase=1&le-page=1&ls-page=1'
    r = requests.get(url)
    jsonResponse = r.json()
    users = jsonResponse["standings"]["results"]
    league_name = jsonResponse["league"]["name"]

    return league_name, users

    
if __name__ == "__main__":
    
    url = 'https://fantasy.premierleague.com/drf/entry/' + str(1)
    r = requests.get(url)
    jsonResponse = r.json()
    data = jsonResponse["entry"]
    gw = data['current_event']

    users = session.query(Users.user_id, Teams.team_name, Teams.team_id).join(Teams, Teams.user_id == Users.user_id).group_by(Users.user_id, Teams.team_name, Teams.team_id).all()
    #print users
    #league_users = [u[0] for u in users]
    
    for u in users:
        team_stats = get_user_info(u, gw)   
        print(team_stats.rank_gw)
        gw_stats = session.query(Stats).filter(Stats.team_id==u[2]).filter(Stats.gameweek==team_stats.gameweek).first()
        #gw_stats = session.query(Stats).all()
        #print gw_stats
        #print team_stats
        #print len(gw_stats)
        if gw_stats:
            gw_stats.points = team_stats.points
            gw_stats.team_value = team_stats.team_value
            gw_stats.bank_money = team_stats.bank_money
            gw_stats.rank = team_stats.rank
            gw_stats.rank_gw = team_stats.rank_gw
        else:
            session.add(team_stats)
        # get the user object and update the points by summing up all gw points
        user_update = session.query(Users).filter(Users.season==13).filter(Users.user_id==u[0]).first()
        user_gws = session.query(Stats).filter(Stats.team_id==u[2])
        user_points = sum(u.points for u in user_gws)
        user_update.points = user_points
    session.commit()
    #conn = sqlite3.connect(sqlite_file)
    #c = conn.cursor()
    #conn.commit()
    #conn.close()
