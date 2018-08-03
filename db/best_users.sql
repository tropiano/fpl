select u.name, u.surname, u.points, u.season, u.season_name from teams t
join users u on u.user_id = t.user_id
order by u.points desc
limit 5;

select u.name, u.surname, u.rank, u.season, u.season_name from teams t
join users u on u.user_id = t.user_id
order by u.rank
limit 5;
