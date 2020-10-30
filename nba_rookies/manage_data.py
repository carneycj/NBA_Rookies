import os
import pandas as pd
import pyodbc
from sklearn.pipeline import Pipeline

# Support package for data cleaning
import support.cleaning_pipe as cp

TO_PM = [
    "fg",
    "threes",
    "ft",
    "orb",
    "trb",
    "ast",
    "stl",
    "blk",
    "tov",
    "pf",
    "pts",
]
DROP_COLS = [
    "mp_pg",
    "fga",
    "threes_a",
    "fta",
    "trb_pg",
    "ast_pg",
    "pts_pg",
    "yr1",
    "retired",
    "g",
    "debut",
]


def clean_data(df, to_pm=TO_PM, drop_cols=DROP_COLS, min_seasons=5):
    """
    This function is responsible for taking a dataframe and cleaning it, then
    returning a cleaned dataframe.
    """
    cleaning_pipe = Pipeline(
        [
            ("to_per_minute", cp.ToPerMinute(to_pm)),
            ("fill_na", cp.FillNA()),
            ("drop_columns", cp.DropFeatures(drop_cols)),
            ("create_labels", cp.CreateLabels(min_seasons)),
        ]
    )
    return cleaning_pipe.fit_transform(df)


# TODO This needs to enter the cleaned data into sql
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


def manage_data(filename="rookies_stats.csv"):
    """
    This is the main function that takes that rookie data, cleans it, and then
    outputs the cleaned data into a cleaned .csv, as well as into a SQL
    database.
    """
    dirty_rookies = pd.read_csv(os.path.join("data", filename))
    cleaned_rookies = clean_data(dirty_rookies)
    cleaned_rookies.to_csv(os.path.join("data", f"cleaned_{filename}"))


if __name__ == "__main__":
    manage_data()
