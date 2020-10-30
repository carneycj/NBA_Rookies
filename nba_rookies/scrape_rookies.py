import datetime
import numpy as np
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
    this_month = datetime.date.today().month

    if (this_month >= 10) and (this_year != 2020):
        """
        We need to consider the start of the new season in october.  If I say
        2020, that means the 2020 playoff season, so if it's after the start of
        the new season, we need to push the year forward one.  The 2020-2021
        season starts in December/January, so we will have to look at this again
        once the season actually starts and handle that edge case then (since
        they aren't totally sure when they'll start)
        """
        this_year += 1

    players = [
        [value.text for value in tr]
        for tr in season_soup.find("tbody")("tr", {"class": "full_table"})
    ]
    seasons = _career_stats(career_soup)
    for index, player in enumerate(players):
        player[4] = seasons[index]  # Total seasons played by the player
        retired = 1 if (this_year - year) > (int(seasons[index]) - 1) else 0
        player.extend([int(year), retired])

    return players


"""
--------------------------------------------------------------------------------
The fourth task is to store all the raw data into a .csv.
"""


def data_to_csv(df, filename):
    """
    This function enters all of the data into 'rookies_stats.csv', which is
    stored in the folder 'data'.
    """
    df.to_csv(os.path.join("data", filename), index=False)


"""
--------------------------------------------------------------------------------
Main body of code for the scraping of rookie data.
"""


def scrape_rookies(start_year=2000, end_year=2015):
    """
    This is our main function for sraping the rookies.  There are defaul values
    for simplicity.

    Note: the year in the url is the year of the playoffs for that season
        - This means that start_year=2000 is the '99-'00 season
    """
    years = [x for x in range(start_year, end_year + 1)]

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


if __name__ == "__main__":
    scrape_rookies()
