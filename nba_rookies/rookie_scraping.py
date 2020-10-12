import csv
import os
import requests

from bs4 import BeautifulSoup


"""
This program scrapes data from two websites and pushes the information into csv
files.
"""

# The years can potentially be modified at some point to allow me to get data
# for different years and not have to change too much code
YEARS = [x for x in range(2000, 2015)]

LINK_DIFFS = ["season", "career"]

# 2 is their debut game, which isn't important.
# 4 is years played, which is pulled from a second site.
# Do not change the index of 4 (IGNORE_COLS[1]), it is required in the program.
IGNORE_COLS = [2, 4]

"""
--------------------------------------------------------------------------------
The first task is to collect and organize the columns that will be used, as well
as the descriptions for each column.
"""


def create_header():
    with open(os.path.join("data", "table_headers.csv"), "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        source = requests.get(
            f"https://www.basketball-reference.com/leagues/NBA_{YEARS[0] + 1}_rookies-{LINK_DIFFS[0]}-stats.html"
        ).text
        soup = BeautifulSoup(source, "lxml")

        headers = soup.find("thead").find_all("tr")[1]
        ignores = [x * 2 + 1 for x in IGNORE_COLS]
        # We need these renames to be able to work with the data effectively in
        # the future.  Now they are unique column names
        col_renames = [x * 2 + 1 for x in [24, 25, 26, 27]]
        for index, header in enumerate(headers, start=0):
            try:
                if (index not in ignores) and (index not in col_renames):
                    header_name = header.text
                    header_desc = header.get("aria-label")
                    csv_writer.writerow([header_name, header_desc])
                elif index == ignores[1]:
                    header_name = "Yrs"
                    header_desc = "Years in the NBA"
                    csv_writer.writerow([header_name, header_desc])
                elif index == col_renames[0]:
                    header_name = "MPPG"
                    header_desc = header.get("aria-label")
                    csv_writer.writerow([header_name, header_desc])
                elif index == col_renames[1]:
                    header_name = "PPG"
                    header_desc = header.get("aria-label")
                    csv_writer.writerow([header_name, header_desc])
                elif index == col_renames[2]:
                    header_name = "TRBPG"
                    header_desc = header.get("aria-label")
                    csv_writer.writerow([header_name, header_desc])
                elif index == col_renames[3]:
                    header_name = "ASTPG"
                    header_desc = header.get("aria-label")
                    csv_writer.writerow([header_name, header_desc])
            except:
                pass


"""
--------------------------------------------------------------------------------
The second task is to collect and organize all of the rookies and their stats
from the website by year.
"""


def one_stat(year, master_index):
    """
    The purpose of this function is to grab the one value needed from the second
    website, and return it.
    """
    lk_ind = 1
    source = requests.get(
        f"https://www.basketball-reference.com/leagues/NBA_{year + 1}_rookies-{LINK_DIFFS[lk_ind]}-stats.html"
    ).text
    soup = BeautifulSoup(source, "lxml")

    players = soup.find("tbody").find_all("tr", class_="full_table")
    row = 0
    for player in players:
        for col, stat in enumerate(player.find_all("td"), start=0):
            if (row == master_index[0]) and (col == master_index[1]):
                return stat.text
        row += 1


def stats_seps(year):
    """
    This function pulls all of the stats for the player's rookie season and
    pushes it to a csv file for the year.
    """
    master_index = [0, 0]
    lk_ind = 0

    with open(
        os.path.join("data", f"rookies_{year}.csv"), "w", newline="",
    ) as csv_file:
        csv_writer = csv.writer(csv_file)
        source = requests.get(
            f"https://www.basketball-reference.com/leagues/NBA_{year + 1}_rookies-{LINK_DIFFS[lk_ind]}-stats.html"
        ).text
        soup = BeautifulSoup(source, "lxml")

        players = soup.find("tbody").find_all("tr", class_="full_table")
        ignores = [x - 1 for x in IGNORE_COLS]
        isascii = lambda s: len(s) == len(s.encode())
        for player in players:
            stats = list()
            if master_index[1] == 0:
                stats.append(player.th.text)
            for master_index[1], stat in enumerate(player.find_all("td"), start=0):
                if master_index[1] not in ignores:
                    if isascii(stat.text):
                        stats.append(stat.text)
                    else:
                        new_stat = ""
                        for char in stat.text:
                            if isascii(char):
                                new_stat += char
                            else:
                                new_stat += "_"
                        stats.append(new_stat)
                elif master_index[1] == ignores[1]:
                    stats.append(one_stat(year, master_index))

            csv_writer.writerow(stats)
            master_index = [master_index[0] + 1, 0]
        return


"""
--------------------------------------------------------------------------------
The third task is to join each of the 'rookies_*year*.csv' together into
'rookies_stats.csv' and append each rookie's stats row with the year they
started.
"""


def comb_csvs():
    with open(
        os.path.join("data", f"rookies_stats.csv"), "w", newline=""
    ) as csv_file_comb:
        csv_writer = csv.writer(csv_file_comb)
        for year in YEARS:
            with open(os.path.join("data", f"rookies_{year}.csv")) as csv_file_year:
                csv_reader = csv.reader(csv_file_year)
                for row in csv_reader:
                    row = [str(stat) for stat in row]
                    row.append(year)
                    csv_writer.writerow(row)


def append_header():
    with open(os.path.join("data", "table_headers.csv"), "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        header_name = "Yr"
        header_desc = "Player Starting Year"
        csv_writer.writerow([header_name, header_desc])


if __name__ == "__main__":
    create_header()
    append_header()
    for year in YEARS:
        stats_seps(year)
    comb_csvs()
