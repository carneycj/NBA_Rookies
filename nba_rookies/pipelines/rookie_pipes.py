from sklearn.base import BaseEstimator, TransformerMixin


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
}


class DropColumns(BaseEstimator, TransformerMixin):
    """
    This class is used to take a dataframe and from the columns that you don't
    want from it.  It accepts a list of columns that it then uses to remove the
    appropriate features.
    """

    def __init__(self, drop_cols=None):
        self.drop_cols = drop_cols

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_.drop(columns=self.drop_cols, inplace=True)
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
        X_["debut"] = X_["debut"].apply(lambda month: month[:3].lower()).map(month_map)
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

