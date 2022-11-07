import yfinance as yf
import pyqtgraph as pg
from datetime import datetime
import numpy as np
from scipy.stats import norm


# Architecture issue with sklearn, self implement a limited version of LinearRegression
class LinearRegression:
    def __init__(self):
        self.w = np.array([])
        self.std_scale = np.array([])
        self.mean_scale = np.array([])

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        assert len(X.shape) == 2
        assert len(y.shape) == 1
        assert X.shape[0] == y.shape[0]

        # Setup fitting
        self.fit_setup(X)

        # Augment data to include bias feature
        X = self.transform(X)

        self.w = np.ones(X.shape[1]) * 0.5
        print(self.w)

        # Check condition number
        A = np.matmul(X.transpose(), X)
        Ainv = np.linalg.inv(A)

        k = np.linalg.norm(A) * np.linalg.norm(Ainv)
        print("Condition number: ", k)

        # Perform fitting
        self.w = np.dot(y, np.matmul(Ainv, X.transpose()).transpose())
        return self

    def predict(self, X):
        X = self.transform(X)

        # Calculate predictions
        return np.dot(X, self.w)

    def fit_setup(self, X):
        # Calculate rescaling
        self.std_scale = np.ones(X.shape[1] + 1)
        self.mean_scale = np.ones(X.shape[1] + 1)
        for col in range(X.shape[1]):
            self.std_scale[col] = np.std(X[:, col])
            self.mean_scale[col] = np.mean(X[:, col])
        self.std_scale[-1] = 1
        self.mean_scale[-1] = 0

    def transform(self, X):
        # Add bias feature
        X_new = np.concatenate((X, np.ones((X.shape[0], 1))), axis=1)

        # Rescale
        for col in range(X_new.shape[1]):
            X_new[:, col] = (X_new[:, col] - self.mean_scale[col]) / self.std_scale[col]

        return X_new


class Data:
    def __init__(self, ticker):
        # Fetch data
        self.data = yf.Ticker(ticker)
        self.df = self.data.history(period="max")
        self.df["Timestamp"] = [x.to_pydatetime().timestamp() for x in self.df.index]

        # Other attributes
        #    self.reg : LinearRegression model in fitting
        #    self.std : Standard deviation using model predictions as a mean estimation
        #    self.xpred : Timestamps used in prediction
        #    self.ypred : Prediction results
        #    self.sigma_factor : Factor of sigma for setting upper and lower bounds
        #    self.upperbound, self.lowerbound : Bounds based on sigma_factor used. Same size as self.xpred

    def ln(self):
        np.seterr(divide="ignore")
        self.df[["Open", "High", "Low", "Close"]] = self.df[["Open", "High", "Low", "Close"]].apply(lambda x: np.log(x))

    def get_data(self, col):
        return self.df["Timestamp"], self.df[col]

    def get_confidence(self, col, conf_interval, lowerdate, upperdate):
        # Truncate data
        lower = lowerdate.toPyDateTime().timestamp()
        upper = upperdate.toPyDateTime().timestamp()

        self.df_trunc = self.df.drop(self.df[self.df["Timestamp"] < lower].index)
        self.df_trunc = self.df_trunc.drop(self.df_trunc[self.df_trunc["Timestamp"] > upper].index)

        # Linear regression
        self.X = np.array([self.df_trunc["Timestamp"]]).transpose()
        self.y = np.array(self.df_trunc[col])

        self.reg = LinearRegression().fit(self.X, self.y)

        # Predict
        self.xpred = np.array(self.df["Timestamp"])
        self.ypred = self.reg.predict(np.array([self.xpred]).transpose())

        # Calculate std
        self.std = np.std(self.y - self.reg.predict(self.X))

        # Get bounds
        cdf_percentile = (conf_interval + 1)/2
        self.sigma_factor = norm.ppf(cdf_percentile)

        self.upperbound = self.ypred + self.std * self.sigma_factor
        self.lowerbound = self.ypred - self.std * self.sigma_factor

        return self.xpred, self.ypred, self.lowerbound, self.upperbound


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value) for value in values]

