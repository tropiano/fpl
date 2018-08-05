import sqlite3
#import pandas as pd
#import model
import requests

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


if __name__ == "__main__":
    sqlite_file = '../db/fpl.db'
    league_id = 153875 #177825 #
    league_name, league_users = get_league_infos(league_id)
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO leagues (season, league_id, league_name) VALUES (?, ?, ?)", ('18-19', league_id, league_name))    
        
        for u in league_users:
            team_info = (u['id'], u['league'], u['entry_name'], u['entry'])
            c.execute("INSERT INTO teams (team_id, league_id, team_name, user_id) VALUES (?, ?, ?, ?)", team_info)
            user_info = extract_user_infos(u)
            for ui in user_info:
                c.execute("INSERT INTO users (user_id, season, season_name, name, surname, points, rank) VALUES (?, ?, ?, ?, ?, ?, ?)", ui)

    except sqlite3.IntegrityError:
        print('ERROR: ID already exists in PRIMARY KEY column')
    
    conn.commit()
    conn.close()
