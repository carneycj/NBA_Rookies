import datetime
import numpy as np
import os
import pandas as pd
import pyodbc
import requests

from bs4 import BeautifulSoup


"""
This program scrapes data from basketball-reference.com to collect rookie
season stats and the total number of seasons that the rookie played
"""


"""
--------------------------------------------------------------------------------
The first task is to connect to the website and create the soup to work with
"""


def create_soup(url):
    """ This function takes a url and creates a soup for us to work with"""
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html5lib")
    return soup


"""
--------------------------------------------------------------------------------
The second task is to create a table that describes each feature and clean the
features for use in the rookie data DataFrame.
"""


def create_header_df(soup):
    """
    This function finds the feature names and their descriptions, puts them
    into a DataFrame, and cleans them for future use.
    """
    headers = [
        (th.text, th.get("aria-label"))
        for th in soup.find("thead").find_all("tr")[1].find_all("th")
    ]
    df_desc = pd.DataFrame(headers, columns=["feature", "description"])
    df_desc["feature"] = df_desc["feature"].apply(lambda x: x.lower())
    df_desc.iloc[9]["feature"] = "threes"
    df_desc.iloc[10]["feature"] = "threes_a"
    df_desc.iloc[21]["feature"] = "fg_pct"
    df_desc.iloc[22]["feature"] = "threes_pct"
    df_desc.iloc[23]["feature"] = "ft_pct"
    df_desc.iloc[24]["feature"] = "mp_pg"
    df_desc.iloc[25]["feature"] = "pts_pg"
    df_desc.iloc[26]["feature"] = "trb_pg"
    df_desc.iloc[27]["feature"] = "ast_pg"
    df_desc.iloc[4]["description"] = "Years Played"
    df_desc = df_desc.append(
        {"feature": "yr1", "description": "Rookie Year"}, ignore_index=True
    )
    df_desc = df_desc.append(
        {"feature": "retired", "description": "Is the player retired (1: yes, 0: no)"},
        ignore_index=True,
    )
    return df_desc


"""
--------------------------------------------------------------------------------
The third task is to collect and organize all of the rookies and their stats
from the website by year.
"""


def _career_stats(career_soup):
    """
    This function collects the number of years the rookie ends up playing and
    returns that value.
    """
    players = [
        [value.text for value in tr]
        for tr in career_soup.find("tbody")("tr", {"class": "full_table"})
    ]
    seasons = [player[4] for player in players]
    return seasons


def rookie_stat_collect(season_soup, career_soup, year):
    """
    This function collects and organizes all of the rookie data into a list of
    lists.
    """
    this_year = datetime.date.today().year

    players = [
        [value.text for value in tr]
        for tr in season_soup.find("tbody")("tr", {"class": "full_table"})
    ]
    seasons = _career_stats(career_soup)
    for index, player in enumerate(players):
        player[4] = seasons[index]  # Total seasons played by the player
        retired = 1 if (this_year - year) > (int(seasons[index]) - 1) else 0
        player.extend([str(year), retired])
        for i, stat in enumerate(player):
            # We want to type this data so that it's easier to work with
            if i in range(21, 28):
                if stat:
                    player[i] = np.float64(stat)
                # We don't want nulls because pyodbc doesn't play well with them
                else:
                    player[i] = np.float64(0.0)
            elif i not in {1, 2}:
                player[i] = np.int64(stat)

    return players


"""
--------------------------------------------------------------------------------
The fourth task is to store all the data in 'rookies_stats.csv' and into a SQL
database.
"""


def data_to_csv(df, filename):
    """
    This function enters all of the data into 'rookies_stats.csv', which is
    stored in the folder 'data'.
    """
    df.to_csv(os.path.join("data", filename), index=False)


# TODO Enter data to database
def data_to_database(df):
    """
    This function takes the dataframe and enters it into a SQL Server Database.
    The Database and the tables have already been created through SQL Queries,
    this is just meant to enter in the data collected.
    """
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=CHRIS-LAPTOP\SQLEXPRESS;"
        "Database=rookie_stat_db;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()

    for index, row in df.iterrows():
        player_id = index + 1

        # Fill the player table
        cursor.execute(
            "INSERT INTO player(id, name) VALUES (?, ?)", player_id, row.player
        )

        # Fill the rookie_info table
        cursor.execute(
            f"INSERT INTO rookie_info (player_id, debut, yr1, age, rk) VALUES (?, ?, ?, ?, ?)",
            player_id,
            row.debut,
            row.yr1,
            row.age,
            row.rk,
        )

        # Fill the career table
        cursor.execute(
            f"INSERT INTO career (player_id, yrs, retired) VALUES (?, ?, ?)",
            player_id,
            row.yrs,
            row.retired,
        )

        # Fill the game_stats table
        cursor.execute(
            f"INSERT INTO game_stats (player_id, g, mp, fg, fga, threes, threes_a, ft, fta, orb, trb, ast, stl, blk, tov, pf, pts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            player_id,
            row.g,
            row.mp,
            row.fg,
            row.fga,
            row.threes,
            row.threes_a,
            row.ft,
            row.fta,
            row.orb,
            row.trb,
            row.ast,
            row.stl,
            row.blk,
            row.tov,
            row.pf,
            row.pts,
        )

        # Fill the pg_stats table
        cursor.execute(
            f"INSERT INTO pg_stats (player_id, mp_pg, trb_pg, ast_pg, pts_pg) VALUES (?, ?, ?, ?, ?)",
            player_id,
            row.mp_pg,
            row.trb_pg,
            row.ast_pg,
            row.pts_pg,
        )

        # Fill the pct_stats table
        cursor.execute(
            f"INSERT INTO pct_stats (player_id, fg_pct, threes_pct, ft_pct) VALUES (?, ?, ?, ?)",
            player_id,
            row.fg_pct,
            row.threes_pct,
            row.ft_pct,
        )

    conn.commit()
    cursor.close()


"""
--------------------------------------------------------------------------------
Main body of code for the scraping of rookie data.
"""


if __name__ == "__main__":
    # Note: the year in the url is the year of the playoffs for that season
    START_YEAR = 2000
    END_YEAR = 2015
    years = [x for x in range(START_YEAR, END_YEAR)]

    for count, year in enumerate(years):
        url_season = f"https://www.basketball-reference.com/leagues/NBA_{year}_rookies-season-stats.html"
        url_career = f"https://www.basketball-reference.com/leagues/NBA_{year}_rookies-career-stats.html"
        season_soup = create_soup(url_season)
        career_soup = create_soup(url_career)
        if count == 0:
            df_desc = create_header_df(season_soup)
            df = pd.DataFrame(columns=df_desc["feature"])

        df_year = pd.DataFrame(
            rookie_stat_collect(season_soup, career_soup, year),
            columns=df_desc["feature"],
        )
        df = df.append(df_year, ignore_index=True)

    data_to_csv(df, "rookies_stats.csv")
    data_to_csv(df_desc, "rookies_stats_desc.csv")
    data_to_database(df)
