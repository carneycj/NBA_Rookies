import datetime
import os
import pandas as pd
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
    df_desc.iloc[21]["feature"] = "fg_pct"
    df_desc.iloc[22]["feature"] = "3p_pct"
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


# TODO get years played
def _career_stats(career_soup, year):
    """
    This function collects the number of years the rookie ends up playing and
    returns that value.
    """
    players = [
        [value.text for value in tr]
        for tr in career_soup.find("tbody")("tr", {"class": "full_table"})
    ]


# TODO add years played, year, and if retired to the correct indexes
def rookie_stat_collect(df, season_soup, career_soup, year):
    """
    This function collects and organizes all of the rookie data into the
    DataFrame.
    """
    this_year = datetime.date.today().year

    players = [
        [value.text for value in tr]
        for tr in season_soup.find("tbody")("tr", {"class": "full_table"})
    ]
    yrs_played = _career_stats(career_soup, year)
    [player.append(str(year)) for player in players]
    print(players)


"""
--------------------------------------------------------------------------------
The fourth task is to join all of the data together and store it in
'rookies_stats.csv' and into a SQL database, appending each rookie's stats row
with the year they started.
"""

# TODO
def append_data():
    pass


# TODO
def append_header():
    pass


# TODO
def to_database():
    pass


"""
--------------------------------------------------------------------------------
Main body of code for the scraping of rookie data.
"""

# TODO
# Note: the year in the url is the year of the playoffs for that season
years = [2011]  # , 2012]  # [x for x in range(2000, 2015)]

url_season = (
    f"https://www.basketball-reference.com/leagues/NBA_2011_rookies-season-stats.html"
)
url_career = (
    f"https://www.basketball-reference.com/leagues/NBA_2011_rookies-career-stats.html"
)

if __name__ == "__main__":
    for count, year in enumerate(years):
        season_soup = create_soup(url_season)
        if count == 0:
            df_desc = create_header_df(season_soup)
            df = pd.DataFrame(columns=df_desc["feature"])

        career_soup = create_soup(url_career)
        df.append(rookie_stat_collect(df, season_soup, career_soup, year))

    # print(df_desc)
    # print(df)
