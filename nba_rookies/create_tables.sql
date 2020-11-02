USE [Rookie_Stat_DB];

DROP TABLE IF EXISTS pm_stats;
DROP TABLE IF EXISTS pct_stats;
DROP TABLE IF EXISTS pg_stats;
DROP TABLE IF EXISTS game_stats;
DROP TABLE IF EXISTS career;
DROP TABLE IF EXISTS rookie_info;
DROP TABLE IF EXISTS player;


CREATE TABLE player
(
	id BIGINT,
	name VARCHAR(75) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE rookie_info
(
	player_id BIGINT UNIQUE,
	debut VARCHAR(75),
	yr1 FLOAT,
	age FLOAT,
	rk FLOAT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE career
(
	player_id BIGINT UNIQUE,
	yrs FLOAT,
	retired FLOAT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE game_stats
(
	player_id BIGINT UNIQUE,
	g BIGINT,
	mp BIGINT,
	fg BIGINT,
	fga BIGINT,
	threes BIGINT,
	threes_a BIGINT,
	ft BIGINT,
	fta BIGINT,
	orb BIGINT,
	trb BIGINT,
	ast BIGINT,
	stl BIGINT,
	blk BIGINT,
	tov BIGINT,
	pf BIGINT,
	pts BIGINT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE pg_stats
(
	player_id BIGINT UNIQUE,
	mp_pg FLOAT,
	trb_pg FLOAT,
	ast_pg FLOAT,
	pts_pg FLOAT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE pct_stats
(
	player_id BIGINT UNIQUE,
	fg_pct FLOAT,
	threes_pct FLOAT,
	ft_pct FLOAT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE pm_stats
(
	player_id BIGINT UNIQUE,
	fg_pm FLOAT,
	threes_pm FLOAT,
	ft_pm FLOAT,
	orb_pm FLOAT,
	trb_pm FLOAT,
	ast_pm FLOAT,
	stl_pm FLOAT,
	blk_pm FLOAT,
	tov_pm FLOAT,
	pf_pm FLOAT,
	pts_pm FLOAT,
	FOREIGN KEY (player_id) REFERENCES player(id)
);
