drop table if exists leagues;
create table leagues(
    id integer primary key autoincrement,
    season text not null,
    league_id integer not null,
    league_name text not null,
    CONSTRAINT c UNIQUE (league_id, league_name)
);

drop table if exists teams;
create table teams(
    id integer primary key autoincrement,
    team_id integer not null,
    league_id integer not null,
    team_name text not null,
    user_id integer not null
);

drop table if exists users;
create table users(
    id integer primary key autoincrement,
    user_id integer not null,
    season text not null,
    season_name text not null,
    name text not null,
    surname text not null,
    points integer not null,
    rank integer not null
);

drop table if exists stats;
create table stats(
    id integer primary key autoincrement,
    team_id integer not null,
    season text not null,
    team_value text not null,
    gameweek integer not null,
    points integer not null,
    best_player text,
    worst_player text,
    best_player_points integer,
    worst_player_points integer
);

drop table if exists players;
create table players(
    id integer primary key autoincrement,
    player_id integer not null,
    player_name text not null,
    player_points integer not null,
    gameweek integer not null,
    user_id text,
    captain integer not null 
);
