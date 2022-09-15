import pandas as pd
import matplotlib.pyplot as plt


class CSVUtils:
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv('csv_files/Bitfinex_ETHUSD_minute.csv')
        self.df = self.df.loc[::-1].reset_index(drop=True)

    def getDF(self):
        return self.df

    def plotDF(self):
        self.df.plot(x='date', y='close', kind='line')
        plt.show()
