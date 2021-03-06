import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin

"""
This file is used to support the rest of the project by storing all of the
pipeline classes/functions that are needed to properly automate the cleaning of
the data collected and whatever future data may be collected.
"""


month_map = {
    "oct": 0,
    "nov": 1,
    "dec": 2,
    "jan": 3,
    "feb": 4,
    "mar": 5,
    "apr": 6,
    "may": 7,
    "jun": 8,
    "jul": 9,
    "aug": 10,
    "sep": 11,
    np.nan: 11,
}


class ToPerMinute(BaseEstimator, TransformerMixin):
    """
    This class is used to take a dataframe and a list of columns that need to
    be converted to a per minute played value.  It then uses that list to
    convert the appropriate features.
    """

    def __init__(self, to_pm=None):
        self.to_pm = to_pm

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        for stat in self.to_pm:
            X_[stat + "_pm"] = round(X_[stat] / X_["mp"], 7)
            X_[stat + "_pm"].fillna(0.0, inplace=True)
        X_.drop(columns=self.to_pm, inplace=True)
        return X_


class GetDebutMonth(BaseEstimator, TransformerMixin):
    """
    This class is used to take the player's debut information and take the month
    from it.  This is then converted to an int, from start to end of the season
    (not calendar year).
    """

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_["debut_month"] = (
            X_["debut"].apply(lambda month: month[:3].lower()).map(month_map)
        )
        return X_


class FillNA(BaseEstimator, TransformerMixin):
    """
    This class is used to take a dataframe and fill all missing values in it
    with 0, since missing values are meant to be 0 on basketball-reference.
    """

    def __init__(self, fill_value=0):
        self.fill_value = fill_value

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_.fillna(self.fill_value, inplace=True)
        return X_


class DropFeatures(BaseEstimator, TransformerMixin):
    """
    This class is used to take a dataframe and a list of columns that you want
    to remove.  It then uses that list to remove the appropriate features.
    """

    def __init__(self, drop_cols=None):
        self.drop_cols = drop_cols

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_.drop(columns=self.drop_cols, inplace=True)
        return X_


class CreateLabels(BaseEstimator, TransformerMixin):
    """
    This is used to convert the years the player has played into the label of if
    the player has played the number of years that you are looking into.  The
    default is 5, but you can change the number if desired.
    """

    def __init__(self, seasons=5):
        self.seasons = seasons

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_["lasts"] = X_["yrs"] >= self.seasons
        X_.drop("yrs", axis=1, inplace=True)
        return X_

